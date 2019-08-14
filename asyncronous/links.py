import json
import asyncio

from sqlalchemy.exc import IntegrityError
from common.logger_custom import logger
from common.models import ProductModel, ReviewModel, Session
from asyncronous.utils import get_soup, get_pages_count, IsRedirectError
from settings import PAGE_PARAM, LINK_SET_PATH
from asyncronous.ProductClass import Product


async def download_item(session, product_soup, category_name):
	db_product = ProductModel(category_description=category_name)
	try:
		product = await Product.from_list_soup(list_soup=product_soup)
		db_product.specs = str(await product.specs)
		db_product.yandex_id = product.id
	except IsRedirectError:
		logger.warning(f'Product is from other shop: {category_name}, {str(product_soup)[:20]}')
		product = await Product.from_other_shop(list_soup=product_soup)
		db_product.other_shop = True
		db_product.other_shop_id = product.id
	db_product.name = product.name
	db_product.detail_url = product.detail_url
	db_product.original_price = product.original_price
	db_product.final_price = product.final_price

	session.add(db_product)
	for rv in await product.reviews:
		db_review = ReviewModel(**rv.model_data, product=db_product)
		session.add(db_review)

	try:
		session.commit()
	except IntegrityError as e:
		logger.warning(f'Integrity error for category_name: {category_name} {product.detail_url}')
		logger.warning(f'Integrity error for category_name: {product.name}#{product.id}')
		session.rollback()
		session.flush()


# logger.critical('For test purposes continue...')
# raise e


async def download_link(soup, category_name=None):
	session = Session()
	product_list = soup.find('div', 'n-snippet-list').find_all('div', 'n-snippet-card2', recursive=False)

	logger.debug('download_link got {} items'.format(len(product_list)))

	tasks = []
	for i in product_list:
		tasks.append(asyncio.create_task(download_item(session=session, product_soup=i, category_name=category_name)))

	print('LOOP END')
	await asyncio.gather(*tasks)


async def download_page(url_object):
	category_name, url = url_object.get('category_name'), url_object['url']
	# try: #todo: remove all tries like that
	soup = await get_soup(url)
	# if not soup:
	# 	logger.error(f'{category_name}, {url}')
	# 	raise TypeError
	# except (ConnectionError, TimeoutError):
	# 	logger.critical(f'Some shit happened to url: {url} :: 64')
	# 	return
	pages_count = get_pages_count(soup)

	logger.debug(f'Found {pages_count} pages for list url {url}')
	logger.debug('download_page::getting data from page 1')

	tasks = [asyncio.create_task(download_link(soup, category_name))]

	for page_num in range(2, pages_count + 1):
		logger.debug(f'download_list::getting data from page {page_num}')
		new_url = '{}&{}'.format(url, PAGE_PARAM.format(page_num))
		soup = await get_soup(new_url)
		tasks.append(asyncio.create_task(download_link(soup, category_name)))

	await asyncio.gather(*tasks)


async def main(link_set):
	while link_set:
		url_object_form_json = link_set.pop()
		logger.debug(f'url_object_form_json {str(url_object_form_json)}')
		tasks.append(asyncio.create_task(download_page(url_object_form_json)))
	# print(tasks)
	await asyncio.gather(*tasks)


if __name__ == '__main__':
	ls = json.load(open(LINK_SET_PATH, 'r', encoding='utf8'))
	ls = ls[9:11]
	logger.info('START\n')
	tasks = []
	asyncio.run(main(ls), debug=True)
