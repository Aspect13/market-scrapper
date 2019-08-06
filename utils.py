import requests
import json
from bs4 import BeautifulSoup
from uuid import uuid4
from time import sleep

from logger_custom import logger

CACHED_FOLDER = 'cached'


def get_data(url):
	cache_dict_file = 'cache_dict.json'
	cache_dict = json.load(open(cache_dict_file, 'r'))
	file_name = cache_dict.get(url, None)
	if not file_name:
		file_name = '{}.html'.format(str(uuid4())[:8])
		contents = cache_html(url, file_name)
		cache_dict[url] = file_name
		json.dump(cache_dict, open(cache_dict_file, 'w'))
	else:
		try:
			contents = open('{}/{}'.format(CACHED_FOLDER, file_name), 'r').read()
			logger.info('Using cached: {} for url: {}'.format(file_name, url))
		except FileNotFoundError:
			del cache_dict[url]
			json.dump(cache_dict, open(cache_dict_file, 'w'))
			return get_data(url)
	return contents


def cache_html(url, name, attempts=1):
	MAX_GET_ATTEMPTS = 3
	TIMEOUT_SEC = 10

	if attempts > MAX_GET_ATTEMPTS:
		logger.critical(f'Tried {MAX_GET_ATTEMPTS} times to get URL {url}')
		raise TimeoutError(f'Tried {MAX_GET_ATTEMPTS} times to get URL {url}')
	logger.info(f'GETting: {url}\nattempt: {attempts}')
	site = requests.get(url)
	if is_captcha(site.content):
		logger.warning(f'!!! Got captcha for url: {url}\nsleeping for {TIMEOUT_SEC}s...')
		sleep(TIMEOUT_SEC)
		return cache_html(url, name, attempts=attempts+1)
	with open(f'{CACHED_FOLDER}/{name}', 'wb') as out:
		out.write(site.content)
	logger.info(f'Cache name: {name}')
	return site.content


def is_captcha(html):
	return b'<a class="link" href="//yandex.ru/support/captcha/"' in html


def get_soup(url):
	try: #todo: remove all tries like that
		site_data = get_data(url)
	except Exception as e:
		logger.critical(f'Some other shit {e.args} happened to url for {url} :: 59')
		return
	# site_data = get_data(url)
	return BeautifulSoup(site_data, 'html.parser')


def get_pages_count(soup):
	pagebar = soup.find('div', 'n-pager')
	if pagebar:
		return int(json.loads(pagebar['data-bem'])['n-pager']['pagesCount'])
	return 1
