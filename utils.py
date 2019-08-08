from pathlib import Path

import requests
import json
from bs4 import BeautifulSoup
from uuid import uuid4
from time import sleep

from logger_custom import logger

CACHED_FOLDER = 'cached'


class IsRedirectError(Exception):
	# def __init__(self, *args, **kwargs):
	# 	print('IsRedirectError', args, kwargs)
	# 	pass
	msg = 'Link is a redirect'


def get_data(url):
	if is_redirect(url):
		logger.warning(f'URL is a redirect: {url}')
		raise IsRedirectError
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
			contents = open(f'{CACHED_FOLDER}/{file_name}', 'r').read()
			logger.info(f'Using cached: {file_name} for url: {url}')
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
	logger.info(f'GET: {url}')
	if attempts > 1:
		logger.info(f'attempt: {attempts}')
	site = requests.get(url)
	site.encoding = 'utf-8'
	if is_captcha(site.content):
		logger.warning(f'Captcha received for url: {url}')
		logger.warning(f'sleeping for {TIMEOUT_SEC}s...')
		sleep(TIMEOUT_SEC)
		return cache_html(url, name, attempts=attempts+1)
	with open(f'{CACHED_FOLDER}/{name}', 'wb') as out:
		out.write(site.content)
	logger.info(f'Cache name: {name}')
	return site.content


def is_captcha(html):
	return b'<a class="link" href="//yandex.ru/support/captcha/"' in html


def is_redirect(url):
	return '/redir/' in url


def get_soup(url):
	site_data = get_data(url)
	# site_data = get_data(url)
	return BeautifulSoup(site_data, 'html.parser')


def get_pages_count(soup):
	pagebar = soup.find('div', 'n-pager')
	if pagebar:
		return int(json.loads(pagebar['data-bem'])['n-pager']['pagesCount'])
	return 1


def write_tmp_soup(soup):
	with open(f'{Path(__file__).absolute().parent}/sitecache.html', 'w') as out:
		out.write(soup.prettify())
