from urllib.parse import urlparse

# import requests
import json
from datetime import datetime
from pip._internal.utils.misc import cached_property

# from syncronous.utils import get_soup, get_pages_count, write_tmp_soup
from common.logger_custom import logger

# import locale
# locale.setlocale(locale.LC_TIME, ('RU', 'UTF8'))
from common.misc import add_schema
from settings import PAGE_PARAM
from syncronous.utils import get_soup, get_pages_count, write_tmp_soup, download_image


class Product:
	@classmethod
	def from_list_soup(cls, list_soup):
		Item = cls()
		Item.soup = list_soup
		title = list_soup.find('div', 'n-snippet-card2__title')
		Item.name = title.a['title']
		href = urlparse(title.a['href'])
		Item.detail_url = 'https://market.yandex.ru{path}/spec?{query}'.format(path=href.path, query=href.query)
		Item.id = json.loads(list_soup['data-bem'])['n-snippet-card2']['modelId']
		Item.img_url = add_schema(list_soup.find('img')['src'])
		Item._get_prices(list_soup.find_all('div', 'price'))
		Item._get_reviews()
		return Item

	@classmethod
	def from_detail_url(cls, url):
		Item = cls()
		Item.detail_url = url
		Item.soup = Item.details
		Item.name = Item.details.find('h1', 'title').string
		Item.id = json.loads(Item.details.find('div', 'n-product-headline')['data-bem'])['n-product-headline']
		Item.img_url = add_schema(Item.details.find('a', '.n-product-headline__view').find('img', 'image')['src'])
		Item._get_prices(*[i.find_all('', 'price') for i in Item.details.find_all('div', 'n-product-default-offer', )])
		Item._get_reviews()
		return Item

	@classmethod
	def from_other_shop(cls, list_soup):
		Item = cls()
		Item.soup = list_soup
		title = list_soup.find('div', 'n-snippet-card2__title')
		Item.name = title.a['title']
		Item.detail_url = f'http:{title.a["href"]}'
		# Item.id = json.loads(list_soup['data-bem'])['n-snippet-card2']['modelId']
		Item.id = list_soup['id']
		Item.img_url = add_schema(list_soup.find('img')['src'])
		Item._get_prices(list_soup.find_all('div', 'price'))
		# Item._get_reviews()
		return Item

	def __init__(self):
		# assert list_soup or detail_url
		self.id = None
		self.detail_url = None
		self.img_url = None

		self.original_price = None
		self.final_price = None

		self.review_url = None
		self.review_number = 0

	def _get_reviews(self):
		self.review_url = self.detail_url.replace('/spec', '/reviews')
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
		return get_soup(self.detail_url)

	@cached_property
	def specs(self):
		return Specs(self.details.find_all('dl', 'n-product-spec'))

	# @property
	# def model_data(self):
	# 	return {
	# 		'yandex_id': self.id,
	# 		'name': self.name,
	# 		'detail_url': self.detail_url,
	# 		'original_price': self.original_price,
	# 		'final_price': self.final_price,
	# 		'specs': str(self.specs),
	# 	}

	def download_image(self):
		return download_image(self.img_url)

	def __repr__(self):
		d = self.__dict__.copy()
		d['specs'] = repr(self.specs)
		return '''
			{name} #{id}
			URL: {detail_url}
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


class ReviewList(list):
	def __init__(self, url):
		self.url = url
		self.soup = get_soup(url)
		self.pages = get_pages_count(self.soup)
		logger.debug('Review pages found: {}'.format(self.pages))
		self.get_reviews_all()

	def get_reviews_all(self):
		logger.debug('ReviewList::getting data from page 1')
		self.get_reviews_from_page(self.soup)
		for page_num in range(2, self.pages + 1):
			new_url = '{}&{}'.format(self.url, PAGE_PARAM.format(page_num))
			logger.debug('ReviewList::getting data from page {}'.format(page_num))
			soup = get_soup(new_url)
			self.get_reviews_from_page(soup)

	def get_reviews_from_page(self, soup):
		review_items = soup.find_all('div', 'n-product-review-item')
		logger.debug('ReviewList got {} items'.format(len(review_items)))
		for i in review_items:
			self.append(Review(i))


class Review:
	PROS_WORD = 'Достоинства:'
	CONS_WORD = 'Недостатки:'
	COMMENT_WORD = 'Комментарий:'

	def __init__(self, soup):
		self.soup = soup
		self.pros = ''
		self.cons = ''
		self.comment = ''

		write_tmp_soup(soup)

		try:
			self.id = soup['data-review-id']
		except KeyError:
			self.id = soup.div['data-review-id']

		data = self.soup.find('div', {'itemprop': 'review'})
		if data:
			logger.debug('Review trying NEW method...')
			self.date = datetime.strptime(data.find('meta', {'itemprop': 'datePublished'})['content'], '%Y-%m-%d')
			self.author = data.find('meta', {'itemprop': 'author'})['content']
			self.description = data.find('meta', {'itemprop': 'description'})['content']
			self.rating = data.find('div', {'itemprop': 'reviewRating'}).find('meta', {'itemprop': 'ratingValue'})['content']
			self.parse_description()
		else:
			logger.debug('Review trying OLD method...')
			self.date = self.process_date_string(soup.find('span', 'n-product-review-item__date-region').string)
			self.author = soup.find('', 'n-product-review-user__name').string
			# self.comment = soup.find('dd', 'n-product-review-item__text').string
			# self.description = f'{self.COMMENT_WORD} {self.comment}'
			self.rating = soup.find('div', 'rating__value').string
			self.process_description_from_markup()

	@staticmethod
	def process_date_string(date_string):

		months_dict = {
			'января': 1,
			'февраля': 2,
			'марта': 3,
			'апреля': 4,
			'мая': 5,
			'июня': 6,
			'июля': 7,
			'августа': 8,
			'сентября': 9,
			'октября': 10,
			'ноября': 11,
			'декабря': 12,
		}
		tmp = date_string.split()
		modified = f'{tmp[0]}-{months_dict[tmp[1].strip(",").lower()]}'
		return datetime.strptime(modified, '%d-%m')

	@staticmethod
	def _extract(substring, tag):
		try:
			return substring in tag.string
		except (TypeError, AttributeError):
			return False

	def process_description_from_markup(self):
		for i in self.soup.find_all('dl', 'n-product-review-item__stat'):
			if self._extract(self.PROS_WORD, i.dt):
				self.pros = i.dd.string
			elif self._extract(self.CONS_WORD, i.dt):
				self.cons = i.dd.string
			else:
				self.comment += i.dd.string + ' '

	def parse_description(self):
		pros_start = self.description.find(self.PROS_WORD)
		cons_start = self.description.find(self.CONS_WORD)
		comment_start = self.description.find(self.COMMENT_WORD)

		cons_end = len(self.description)
		pros_end = len(self.description)
		if comment_start >= 0:
			cons_end = comment_start
			self.comment = self.description[comment_start + len(self.COMMENT_WORD):].strip()
		if cons_start >= 0:
			pros_end = cons_start
			self.cons = self.description[cons_start + len(self.CONS_WORD):cons_end].strip()
		if pros_start >= 0:
			self.pros = self.description[pros_start + len(self.PROS_WORD):pros_end].strip()

	# def __repr__(self):
	# 	return '''
	# 		Author: {author}
	# 		Date: {date}
	# 		Rating: {rating}
	# 			Pros: {pros}
	# 			Cons: {cons}
	# 			Comment: {comment}
	# 	'''.format(**self.__dict__)

	@property
	def model_data(self):
		return {
			'yandex_id': self.id,
			'author': self.author,
			'rating': self.rating,
			'pros': self.pros,
			'cons': self.cons,
			'comment': self.comment,
			'date': self.date,
		}
