import json

from sqlalchemy.exc import IntegrityError

from ProductClass import Product, PAGE_PARAM
from logger_custom import logger
from models import ProductModel, ReviewModel, Session

# browser = webdriver.PhantomJS()
# browser.get(url)
# html = browser.page_source
from utils import get_soup, get_pages_count, IsRedirectError

link_set = json.load(open('link_set.json', 'r', encoding='utf8'))


def download_item(soup, category_name=None):
	session = Session()
	product_list = soup.find('div', 'n-snippet-list').find_all('div', 'n-snippet-card2', recursive=False)

	logger.debug('download_item got {} items'.format(len(product_list)))

	# todo: remove section
	# print('remove section')
	# product = Product(
	# 	detail_url='https://market.yandex.ru/product--barilla-makarony-spaghetti-n-5-500-g/152406314/spec?track=tabs')
	# db_product = ProductModel(**product.model_data, category_description=category_name)
	# session.add(db_product)
	# print('len', len(product.reviews), product.review_number)
	# for rv in product.reviews:
	# 	db_review = ReviewModel(**rv.model_data, product=db_product)
	# 	print(db_review)
	# 	session.add(db_review)
	# session.commit()
	# print('remove section')

	for i in product_list:

		try:
			product = Product(list_soup=i)
		except IsRedirectError:
			logger.critical(f'Redirect error for category: {category_name}, {str(i)[:20]}')
		db_product = ProductModel(**product.model_data, category_description=category_name)
		session.add(db_product)
		# print('len', len(product.reviews), product.review_number)
		for rv in product.reviews:
			db_review = ReviewModel(**rv.model_data, product=db_product)
			session.add(db_review)

		try:
			session.commit()
		except IntegrityError as e:
			logger.critical(f'Integrity error for category_name: {category_name} {product.name}#{product.id} {product.detail_url}')
			session.rollback()
			session.flush()
			logger.critical('For test purposes continue...')
			# raise e
	print('LOOP END')


def download_list(url_object):
	category_name, url = url_object.get('category_name'), url_object['url']
	try: #todo: remove all tries like that
		soup = get_soup(url)
	except (ConnectionError, TimeoutError):
		logger.critical(f'Some shit happened to url: {url} :: 64')
		return
	pages_count = get_pages_count(soup)

	logger.debug(f'Found {pages_count} pages for list url {url}')
	logger.debug('download_list::getting data from page 1')
	download_item(soup, category_name)

	for page_num in range(2, pages_count + 1):
		logger.debug(f'download_list::getting data from page {page_num}')
		new_url = '{}&{}'.format(url, PAGE_PARAM.format(page_num))
		try: #todo: remove all tries like that
			soup = get_soup(new_url)
			download_item(soup, category_name)
		except Exception as e:
			logger.critical(f'Some {e.args} happened to ur {new_url} :: 79')


if __name__ == '__main__':
	logger.info('START\n')
	while link_set:
		url_object_form_json = link_set.pop()
		print('url_object_form_json', url_object_form_json)
		download_list(url_object_form_json)
