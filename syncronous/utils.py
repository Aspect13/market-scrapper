import requests
import json

from bs4 import BeautifulSoup
from uuid import uuid4
from time import sleep
from pathlib import Path

from requests.exceptions import MissingSchema

from common.logger_custom import logger
from common.misc import get_cache_dict
from settings import CACHE_DICT_PATH, CACHED_FOLDER, MAX_GET_ATTEMPTS, TIMEOUT_SEC, SITECACHE_PATH, HEADERS, \
	IMG_CACHE_FOLDER_RELATIVE, ROOT_DIR


class IsRedirectError(Exception):
	# def __init__(self, *args, **kwargs):
	# 	print('IsRedirectError', args, kwargs)
	# 	pass
	msg = 'Link is a redirect'


def get_data(url):
	if is_redirect(url):
		logger.warning(f'URL is a redirect: {url}')
		raise IsRedirectError
	cache_dict = get_cache_dict()
	file_name = cache_dict.get(url, None)
	if not file_name:
		file_name = '{}.html'.format(str(uuid4())[:8])
		contents = cache_html(url, file_name)
		cache_dict[url] = file_name
		json.dump(cache_dict, open(CACHE_DICT_PATH, 'w'))
	else:
		try:
			contents = open(f'{CACHED_FOLDER}/{file_name}', 'r').read()
			logger.info(f'Using cached: {file_name} for url: {url}')
		except FileNotFoundError:
			del cache_dict[url]
			json.dump(cache_dict, open(CACHE_DICT_PATH, 'w'))
			return get_data(url)
	return contents


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


def is_captcha(html):
	return b'<a class="link" href="//yandex.ru/support/captcha/"' in html


def is_redirect(url):
	return '/redir/' in url


def get_soup(url):
	site_data = get_data(url)
	return BeautifulSoup(site_data, 'html.parser')


def get_pages_count(soup):
	pagebar = soup.find('div', 'n-pager')
	if pagebar:
		return int(json.loads(pagebar['data-bem'])['n-pager']['pagesCount'])
	return 1


def write_tmp_soup(soup):
	with open(SITECACHE_PATH, 'w') as out:
		out.write(soup.prettify())


def check_img_downloaded(path):
	from common.models import Session
	from common.models import ProductModel
	s = Session()
	return s.query(ProductModel).filter(ProductModel.img_local_path == str(path)).first()


def get_name_from_img_url(img_url):
	name = None
	for i in reversed(img_url.split('/')):
		if '.' in i:
			name = i
			return name.split('.')[0]
	if not name:
		name = img_url.replace(r'/', '__')

	return name


def get_extention_from_url(url):
	d = {
		'.jpeg': 'jpeg',
		'.png': 'png',
		'.gif': 'gif'
	}
	for k, v in d.items():
		if k in url:
			return v
	return 'jpg'


def download_image(url, name=None):

	# db_path_pattern = Path(IMG_CACHE_FOLDER_RELATIVE, name)

	ext = get_extention_from_url(url)
	if not name:
		name = get_name_from_img_url(url)

	assert name

	try:
		response = requests.get(url)
	except MissingSchema:
		response = requests.get(f'http:{url}')

	full_name = f'{name}.{ext}'
	tested_name = check_img_downloaded(full_name)
	if not tested_name:
		file_index = 1
		save_path = Path(ROOT_DIR, IMG_CACHE_FOLDER_RELATIVE, full_name)
		while save_path.exists():
			logger.warning(f'Save path for img exists: {full_name}')
			full_name = f'{name}_{file_index}.{ext}'
			save_path = Path(ROOT_DIR, IMG_CACHE_FOLDER_RELATIVE, full_name)
			file_index += 1

		with open(save_path, 'wb') as out:
			out.write(response.content)
		return Path(IMG_CACHE_FOLDER_RELATIVE, full_name)
	return tested_name.img_local_path

