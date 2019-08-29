import asyncio
import aiohttp
import json

from bs4 import BeautifulSoup
from uuid import uuid4

from common.logger_custom import logger
from settings import MAX_GET_ATTEMPTS, TIMEOUT_SEC, SITECACHE_PATH, CACHE_DICT_PATH, CACHED_FOLDER, HEADERS





async def fetch(session, url):
	async with session.get(url, headers=HEADERS()) as response:
		return await response.text()


async def get_data(url):
	if is_redirect(url):
		logger.warning(f'URL is a redirect: {url}')
		raise IsRedirectError
	cache_dict = json.load(open(CACHE_DICT_PATH, 'r'))
	file_name = cache_dict.get(url, None)
	if not file_name:
		file_name = '{}.html'.format(str(uuid4())[:8])
		contents = await cache_html(url, file_name)
		cache_dict[url] = file_name
		json.dump(cache_dict, open(CACHE_DICT_PATH, 'w'))
	else:
		try:
			contents = open(f'{CACHED_FOLDER}/{file_name}', 'r').read()
			logger.info(f'Using cached: {file_name} for url: {url}')
		except FileNotFoundError:
			del cache_dict[url]
			json.dump(cache_dict, open(CACHE_DICT_PATH, 'w'))
			return await get_data(url)
	return contents


async def cache_html(url, name, attempts=1):
	if attempts > MAX_GET_ATTEMPTS:
		logger.critical(f'Tried {MAX_GET_ATTEMPTS} times to get URL {url}')
		raise TimeoutError(f'Tried {MAX_GET_ATTEMPTS} times to get URL {url}')
	logger.info(f'GET: {url}')
	if attempts > 1:
		logger.info(f'attempt: {attempts}')
	async with aiohttp.ClientSession() as session:
		site = await fetch(session, url)
		# print('SSSSSSSSSSSs', site)
	if is_captcha(site):
		logger.warning(f'Captcha received for url: {url}')
		logger.warning(f'Sleeping for {TIMEOUT_SEC * attempts}s...')
		await asyncio.sleep(TIMEOUT_SEC * attempts)
		return await cache_html(url, name, attempts=attempts+1)
	with open(f'{CACHED_FOLDER}/{name}', 'w') as out:
		out.write(site)
	logger.info(f'Cache name: {name}')
	return site


def is_captcha(html):
	# return b'<a class="link" href="//yandex.ru/support/captcha/"' in html
	return '<a class="link" href="//yandex.ru/support/captcha/"' in html


def is_redirect(url):
	return '/redir/' in url


async def get_soup(url):
	site_data = await get_data(url)
	# site_data = get_data(url)
	return BeautifulSoup(site_data, 'html.parser')


def get_pages_count(soup):
	pagebar = soup.find('div', 'n-pager')
	if pagebar:
		return int(json.loads(pagebar['data-bem'])['n-pager']['pagesCount'])
	return 1


def write_tmp_soup(soup):
	with open(SITECACHE_PATH, 'w') as out:
		out.write(soup.prettify())
