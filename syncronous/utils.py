import requests
import json

from bs4 import BeautifulSoup
from uuid import uuid4
from time import sleep
from pathlib import Path

from common.logger_custom import logger
from common.misc import get_cache_dict
from settings import CACHE_DICT_PATH, CACHED_FOLDER, MAX_GET_ATTEMPTS, TIMEOUT_SEC, SITECACHE_PATH, HEADERS


def cache_html(url, name, attempts=1):
	# proxies = {
	# 	'http': 'socks5://127.0.0.1:9050',
	# }

	if attempts > MAX_GET_ATTEMPTS:
		logger.critical(f'Tried {MAX_GET_ATTEMPTS} times to get URL {url}')
		raise TimeoutError(f'Tried {MAX_GET_ATTEMPTS} times to get URL {url}')
	logger.info(f'GET: {url}')
	if attempts > 1:
		logger.info(f'attempt: {attempts}')

	site = requests.get(url, headers=HEADERS())
	site.encoding = 'utf-8'

	if is_captcha(site.content):
		logger.warning(f'Captcha received for url: {url}')
		logger.warning(f'sleeping for {TIMEOUT_SEC * attempts}s...')
		sleep(TIMEOUT_SEC * attempts)
		return cache_html(url, name, attempts=attempts+1)

	try:
		with open(Path(CACHED_FOLDER, name), 'wb') as out:
			out.write(site.content)
	except FileNotFoundError:
		import os
		os.mkdir(CACHED_FOLDER)
		with open(Path(CACHED_FOLDER, name), 'wb') as out:
			out.write(site.content)
	logger.info(f'Cache name: {name}')
	return site.content


class IsRedirectError(Exception):
	def __init__(self):
		super().__init__(self, 'Link is a redirect')


def get_unique_file_name(directory, extension, uuid_length=8):
	generate = lambda: '{}.{}'.format(str(uuid4())[:uuid_length], extension)
	file_name = generate()
	while Path.exists(Path(directory, file_name)):
		logger.critical(f'WOW, uuid4 got a duplicate! {file_name}')
		file_name = generate()
	return file_name


def get_data(url, recreate_cache_forced=False, **kwargs):
	cache_dict = get_cache_dict()
	file_name = cache_dict.get(url, None)
	if not file_name:
		# file_name = '{}.html'.format(str(uuid4())[:8])
		file_name = get_unique_file_name(CACHED_FOLDER, 'html')
		contents = cache_html(url, file_name)
		cache_dict[url] = file_name
		json.dump(cache_dict, open(CACHE_DICT_PATH, 'w'))
	else:
		file_path = Path(CACHED_FOLDER, file_name)
		try:
			if recreate_cache_forced:
				Path.unlink(file_path)
				logger.info(f'File: {file_path} removed')
				raise FileNotFoundError
			contents = open(file_path, 'r').read()
			logger.info(f'Using cached: {file_name} for url: {url}')
		except FileNotFoundError:
			del cache_dict[url]
			json.dump(cache_dict, open(CACHE_DICT_PATH, 'w'))
			return get_data(url)
	return contents


def is_captcha(html):
	return b'<a class="link" href="//yandex.ru/support/captcha/"' in html


def is_redirect(url):
	return '/redir/' in url


def get_soup(url, allow_redirects=False, **kwargs):
	if is_redirect(url) and not allow_redirects:
		logger.warning(f'URL is a redirect: {url}')
		raise IsRedirectError
	site_data = get_data(url, **kwargs)
	return BeautifulSoup(site_data, 'html.parser')


def get_pages_count(soup):
	pagebar = soup.find('div', 'n-pager')
	if pagebar:
		return int(json.loads(pagebar['data-bem'])['n-pager']['pagesCount'])
	return 1


def write_tmp_soup(soup):
	with open(SITECACHE_PATH, 'w') as out:
		out.write(soup.prettify())


def get_true_other_shop_url(detail_url):
	soup = get_soup(detail_url, allow_redirects=True)
	return soup.find('a', 'b-redir-warning__link').text


