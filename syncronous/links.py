import json
import random

from sqlalchemy.exc import IntegrityError

from common.misc import get_link_set
from settings import LINK_SET_PATH
from syncronous.ProductClass import Product, PAGE_PARAM
from common.logger_custom import logger
from common.models import ProductModel, ReviewModel, Session

# browser = webdriver.PhantomJS()
# browser.get(url)
# html = browser.page_source
from syncronous.utils import get_soup, get_pages_count, IsRedirectError


def download_item(soup, category_name=None):
	session = Session()
	product_list = soup.find('div', 'n-snippet-list').find_all('div', 'n-snippet-card2', recursive=False)

	logger.debug('download_item got {} items'.format(len(product_list)))

	for i in product_list:
		db_product = ProductModel(category_description=category_name)
		try:
			product = Product.from_list_soup(list_soup=i)
			db_product.specs = str(product.specs)
			db_product.yandex_id = product.id
		except IsRedirectError:
			logger.warning(f'Product is from other shop: {category_name}, {str(i)[:20]}')
			product = Product.from_other_shop(list_soup=i)
			db_product.other_shop = True
			db_product.other_shop_id = product.id
		db_product.name = product.name
		db_product.detail_url = product.detail_url
		db_product.original_price = product.original_price
		db_product.final_price = product.final_price

		tmp = session.query(ProductModel).filter(ProductModel.detail_url == product.detail_url).first() # todo: remove
		if tmp:
			db_product = tmp
		db_product.img_url = product.img_url

		if DOWNLOAD_IMAGES:
			local_img_path = product.download_image(name=db_product.id)
			db_product.img_local_path = str(local_img_path)

		session.add(db_product)
		for rv in product.reviews:
			db_review = ReviewModel(**rv.model_data, product=db_product)
			session.add(db_review)

		try:
			session.commit()
		except IntegrityError as e:
			# logger.warning(f'Integrity error for category_name: {category_name} {product.detail_url}')
			# logger.warning(f'Integrity error for category_name: {product.name}#{product.id}')
			session.rollback()
			session.flush()
			# logger.critical('For test purposes continue...')
			# raise e

	print('LOOP END')


def download_list(url_object):
	category_name, url = url_object.get('category_name'), url_object['url']
	# try: #todo: remove all tries like that
	soup = get_soup(url)
	# except (ConnectionError, TimeoutError):
	# 	logger.critical(f'Some shit happened to url: {url} :: 64')
	# 	return
	pages_count = get_pages_count(soup)

	logger.debug(f'Found {pages_count} pages for list url {url}')
	logger.debug('download_list::getting data from page 1')
	download_item(soup, category_name)

	for page_num in range(2, pages_count + 1):
		logger.debug(f'download_list::getting data from page {page_num}')
		new_url = '{}&{}'.format(url, PAGE_PARAM.format(page_num))
		# try: #todo: remove all tries like that
		soup = get_soup(new_url)
		download_item(soup, category_name)
		# except Exception as e:
		# 	logger.critical(f'Some {e.args} happened to ur {new_url} :: 82')


if __name__ == '__main__':
	link_set = get_link_set()
	# link_set = json.load(open(LINK_SET_PATH, 'r', encoding='utf8'))
	logger.info('START\n')
	random.shuffle(link_set)
	DOWNLOAD_IMAGES = input('Download images? (Y/N)\n').lower() == 'y'
	while link_set:
		url_object_form_json = link_set.pop()
		logger.debug(f'url_object_form_json {str(url_object_form_json)}')
		download_list(url_object_form_json)
