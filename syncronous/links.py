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
from syncronous.utils import get_soup, get_pages_count, IsRedirectError, get_true_other_shop_url


DOWNLOAD_IMAGES = False
RESOLVE_OTHER_SHOP_URL = False


def download_item(soup, session,
                  category_name=None, download_images=DOWNLOAD_IMAGES, resolve_other_shop_url=RESOLVE_OTHER_SHOP_URL):

	db_product = ProductModel(category_description=category_name)
	try:
		product = Product.from_list_soup(list_soup=soup)
		db_product.specs = str(product.specs)
		db_product.yandex_id = product.id
	except IsRedirectError:
		logger.warning(f'Product is from other shop: {category_name}, {str(soup)[:20]}')
		product = Product.from_other_shop(list_soup=soup)
		db_product.other_shop = True
		db_product.other_shop_id = product.id

	db_product.name = product.name
	db_product.detail_url = product.detail_url
	db_product.original_price = product.original_price
	db_product.final_price = product.final_price

	# tmp = session.query(ProductModel).filter(ProductModel.detail_url == product.detail_url).first() # todo: remove
	# if tmp:
	# 	db_product = tmp

	db_product.img_url = product.img_url

	if resolve_other_shop_url and db_product.other_shop:
		# this does a GET
		revealed_url = get_true_other_shop_url(product.detail_url)
		db_product.other_shop_url = revealed_url

	if download_images:
		# this does a GET
		local_img_path = product.download_image()
		db_product.img_filename = str(local_img_path)

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


def download_page(soup, category_name=None):
	session = Session()
	product_list = soup.find('div', 'n-snippet-list').find_all('div', 'n-snippet-card2', recursive=False)

	logger.debug('download_item got {} items'.format(len(product_list)))

	for i in product_list:
		download_item(i, session, category_name)


def download_list_all(url_object):
	category_name, url = url_object.get('category_name'), url_object['url']
	soup = get_soup(url)
	pages_count = get_pages_count(soup)

	logger.debug(f'Found {pages_count} pages for list url {url}')
	logger.debug('download_list::getting data from page 1')
	download_page(soup, category_name)

	for page_num in range(2, pages_count + 1):
		logger.debug(f'download_list::getting data from page {page_num}')
		new_url = '{}&{}'.format(url, PAGE_PARAM.format(page_num))
		soup = get_soup(new_url)
		download_page(soup, category_name)


if __name__ == '__main__':
	link_set = get_link_set()
	# link_set = json.load(open(LINK_SET_PATH, 'r', encoding='utf8'))
	logger.info('START\n')
	# random.shuffle(link_set)
	DOWNLOAD_IMAGES = input('DOWNLOAD_IMAGESs? (Y/N)\n').lower() == 'y'
	RESOLVE_OTHER_SHOP_URL = input('RESOLVE_OTHER_SHOP_URL? (Y/N)\n').lower() == 'y'
	while link_set:
		url_object_form_json = link_set.pop()
		logger.debug(f'url_object_form_json {str(url_object_form_json)}')
		download_list_all(url_object_form_json)
