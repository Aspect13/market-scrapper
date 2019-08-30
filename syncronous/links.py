from sqlalchemy.exc import IntegrityError

from common.misc import get_link_set
from settings import PAGE_PARAM
from syncronous.ProductClass import Product
from common.logger_custom import logger
from common.models import ReviewModel

# browser = webdriver.PhantomJS()
# browser.get(url)
# html = browser.page_source
from syncronous.utils import get_soup, get_pages_count, IsRedirectError


DOWNLOAD_IMAGES = False
RESOLVE_OTHER_SHOP_URL = False


def download_item(soup, category_name=None):
	try:
		product = Product.from_list_soup(list_soup=soup)
	except IsRedirectError:
		logger.warning(f'Product is from other shop: {category_name}, {str(soup)[:20]}')
		product = Product.from_other_shop(list_soup=soup)

	if RESOLVE_OTHER_SHOP_URL and product.is_other_shop:
		product.set_other_shop_true_url()

	if DOWNLOAD_IMAGES:
		product.image.download()

	for rv in product.reviews:
		db_review = ReviewModel(**rv.model_data, product=product.db_instance)
		product.session.add(db_review)

	product.commit()
	print('LOOP END')


def download_page(soup, category_name=None):
	product_list = soup.find('div', 'n-snippet-list').find_all('div', 'n-snippet-card2', recursive=False)

	logger.debug('download_item got {} items'.format(len(product_list)))

	for i in product_list:
		download_item(i, category_name)


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
