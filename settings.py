from fake_useragent import UserAgent # pip install fake-useragent
from pathlib import Path
ROOT_DIR = Path(__file__).parent.absolute()

# cache_html
MAX_GET_ATTEMPTS = 15
TIMEOUT_SEC = 10

# product class
PAGE_PARAM = 'page={}'

# links.py
IO_PATH = Path.joinpath(ROOT_DIR, 'IOs')
LINK_SET_PATH = Path.joinpath(IO_PATH, 'link_set.json')
CACHED_FOLDER = Path.joinpath(ROOT_DIR, 'cached')
IMG_CACHE_FOLDER_RELATIVE = Path('img_cache')
CACHE_DICT_PATH = Path.joinpath(IO_PATH, 'cache_dict.json')
SITECACHE_PATH = Path.joinpath(IO_PATH, 'sitecache.html')
DB_PATH = Path.joinpath(ROOT_DIR, 'my_db.sqlite')
LOG_CONFIG_PATH = Path.joinpath(ROOT_DIR, 'common', 'logging.conf')


# excel export
def EXCEL_WB_PATH(suffix=None, index=0):
	file_name = f'market_dump{suffix}_{index}'
	if Path.exists(Path.joinpath(IO_PATH, f'{file_name}.xlsx')):
		new_index = int(file_name.split('_')[-1]) + 1
		return EXCEL_WB_PATH(suffix, new_index)
	else:
		return Path.joinpath(IO_PATH, f'{file_name}.xlsx')


# utils
# HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
class HEADERS(dict):
	_ua = None
	_HEADERS = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
			'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
			'Cache-Control': 'max-age=0',
			'Connection': 'keep-alive',
			'Cookie': 'yandexuid=6940113971567025205; yp=1882385293.yrtsi.1567025293; i=6W+R2uCER1RvWo8dgOZTKZMtH7u/9UcOCX0hAzaH77IB3BDPsTZw6+Jk1kLZgdVHw6y0bquco5nL2fekCzYTtx0unwk=',

			# 'Accept-Encoding': 'gzip, deflate, br',
			# 'DNT': '1',
			# 'Host': 'market.yandex.ru',
			# 'Sec-Fetch-Mode': 'navigate',
			# 'Sec-Fetch-Site': 'none',
			# 'Sec-Fetch-User': '?1',
			# 'Upgrade-Insecure-Requests': '1',
		}

	def __init__(self):
		super().__init__()
		self.update(self._HEADERS)
		self.reroll()

	def reroll(self):
		try:
			self.update({'User-Agent': HEADERS._ua.random})
		except AttributeError:
			HEADERS._ua = UserAgent()
			self.reroll()





# if __name__ == '__main__':
# 	x = HEADERS()
# 	y = HEADERS()
# 	print('x',x['User-Agent'])
# 	print('y',y['User-Agent'])
# 	print(ROOT_DIR)
