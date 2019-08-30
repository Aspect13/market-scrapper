from urllib.parse import urlparse
import json
from pip._internal.utils.misc import cached_property
# import locale
# locale.setlocale(locale.LC_TIME, ('RU', 'UTF8'))
from sqlalchemy import or_

from common.logger_custom import logger
from common.models import ProductModel, ConnectedToModel

from syncronous.ImageClass import Image
from syncronous.ReviewClass import ReviewList
from syncronous.utils import get_soup


class Product(ConnectedToModel):
	MAPPER = (
		('category_description', 'category_description'),
		('specs', 'specs'),
		('yandex_id', 'id'),
		('other_shop', 'is_other_shop'),
		('name', 'name'),
		('detail_url', 'detail_url'),
		('detail_url_query', 'detail_url_query'),
		('original_price', 'original_price'),
		('final_price', 'final_price'),
		('image_id', 'image_id'),
	)

	@classmethod
	def from_list_soup(cls, list_soup, **kwargs):
		Item = cls(category_description=kwargs.get('category_description'))
		Item.soup = list_soup
		title = list_soup.find('div', 'n-snippet-card2__title')
		Item.name = title.a['title']
		url_parsed = urlparse(title.a['href'])
		Item.detail_url = 'https://market.yandex.ru{path}/spec'.format(path=url_parsed.path)
		Item.detail_url_query = url_parsed.query
		Item.id = json.loads(list_soup['data-bem'])['n-snippet-card2']['modelId']
		Item.image_url = list_soup.find('img')['src']
		Item._get_prices(list_soup.find_all('div', 'price'))
		Item._get_reviews()
		return Item

	@classmethod
	def from_detail_url(cls, url, **kwargs):
		Item = cls(category_description=kwargs.get('category_description'))
		url_parsed = urlparse(url)
		Item.detail_url = f'{url_parsed.scheme}://{url_parsed.netloc}{url_parsed.path}'
		Item.detail_url_query = url_parsed.query
		Item.soup = Item.details
		Item.name = Item.details.find('h1', 'title').string
		Item.id = json.loads(Item.details.find('div', 'n-product-headline')['data-bem'])['n-product-headline']
		Item.image_url = Item.details.find('a', 'n-product-headline__view').find('img', 'image')['src']
		Item._get_prices(*[i.find_all('', 'price') for i in Item.details.find_all('div', 'n-product-default-offer', )])
		Item._get_reviews()
		return Item

	@classmethod
	def from_other_shop(cls, list_soup, **kwargs):
		Item = cls(category_description=kwargs.get('category_description'))
		Item.soup = list_soup
		Item.is_other_shop = True
		title = list_soup.find('div', 'n-snippet-card2__title')
		Item.name = title.a['title']
		url_parsed = urlparse(title.a['href'])
		Item.detail_url = f'http://{url_parsed.netloc}{url_parsed.path}'
		Item.detail_url_query = url_parsed.query
		# Item.id = json.loads(list_soup['data-bem'])['n-snippet-card2']['modelId']
		Item.id = list_soup['id']
		Item.image_url = list_soup.find('img')['src']
		Item._get_prices(list_soup.find_all('div', 'price'))
		# Item._get_reviews()
		return Item

	def __init__(self, category_description=None):
		super().__init__(ProductModel)
		self.__db_instance = None
		self.category_description = category_description
		# assert list_soup or detail_url
		self.is_other_shop = False

		self.id = None
		self.detail_url = ''
		self.detail_url_query = ''
		self.image_url = None

		self.original_price = None
		self.final_price = None

		self.review_url = None
		self.review_number = 0

	@property
	def image_id(self):
		return self.image.db_instance.id

	def commit(self):
		something_changed = False
		if not self.image.exists:
			self.image.commit()
		for k, v in self.MAPPER:
			k_value, v_value = self.db_instance.__getattribute__(k), self.__getattribute__(v)
			if str(k_value) != str(v_value):
				self.db_instance.__setattr__(k, self.__getattribute__(v))
				something_changed = True
				logger.info(k, ' changed from ', k_value, ' to ', v_value)
		if something_changed:
			self.session.add(self.db_instance)
			self.session.commit()
		else:
			print(f'Nothing was changed for {self.db_instance.id}')

	@property
	def exists(self):
		return bool(self.db_instance.id)

	@property
	def db_instance(self):
		if self.__db_instance:
			return self.__db_instance
		self.__db_instance = self.session.query(self.model).filter(
			or_(self.model.detail_url == self.detail_url, self.model.yandex_id == self.id)
		).first()
		if not self.__db_instance:
			self.__db_instance = self.model(detail_url=self.detail_url)
		return self.__db_instance

	@cached_property
	def image(self):
		return Image(self.image_url)

	def set_other_shop_true_url(self):
		self.db_instance.other_shop_url = self.true_other_shop_url
		self.commit()

	@property
	def detail_url_full(self):
		if self.detail_url_query == '':
			return self.detail_url
		return f'{self.detail_url}?{self.detail_url_query}'

	@property
	def true_other_shop_url(self):
		return self.details.find('a', 'b-redir-warning__link').text

	def _get_reviews(self):
		if self.is_other_shop:
			return
		self.review_url = self.detail_url_full.replace('/spec', '/reviews')
		try:
			self.review_number = int(self.details.find('a', 'reviews').string.split()[0])
		except AttributeError:
			self.review_number = 0

	@cached_property
	def reviews(self):
		if self.review_number > 0:
			return ReviewList(self.review_url)
		return []

	def _get_prices(self, price_soup):
		if len(price_soup) > 1:
			for price in price_soup:
				if 'unactual' in str(price):
					self.original_price = self.process_price(price.string)
				else:
					self.final_price = self.process_price(price.string)
		else:
			self.original_price, self.final_price = self.process_price(price_soup[0].string), self.process_price(
				price_soup[0].string)

	@staticmethod
	def process_price(price):
		return int(price.strip('от₽  ').replace(' ', ''))
		# return price.strip('₽').strip()
		# return price.split()[0]

	@cached_property
	def details(self):
		#todo fix other_shop_url redirects to actual sites
		return get_soup(self.detail_url_full, allow_redirects=self.is_other_shop)

	@cached_property
	def _specs(self):
		return Specs(self.details.find_all('dl', 'n-product-spec'))

	@cached_property
	def specs(self):
		return str(self._specs)

	def __repr__(self):
		d = self.__dict__.copy()
		d['specs'] = repr(self.specs)
		return '''
			{name} #{id}
			URL: {detail_url_full}
			Prices: {original_price}, {final_price}
			Reviews: {review_number}
		'''.format(**d)
		# '''.format(**self.__dict__, specs=repr(self.specs))


class Specs(list):
	def __init__(self, soup):
		super().__init__(('{}: {}'.format(spec.dt.span.string, spec.dd.span.string) for spec in soup))

	def __repr__(self):
		return '\n\t\t\t\t\t'.join(self)

	def __str__(self):
		return '\n'.join(self)
