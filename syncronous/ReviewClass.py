from datetime import datetime

from common.logger_custom import logger
from settings import PAGE_PARAM
from syncronous.utils import get_soup, get_pages_count


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

		# write_tmp_soup(soup)

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
