from fake_useragent import UserAgent # pip install fake-useragent
from pathlib import Path
ROOT_DIR = Path(__file__).parent.absolute()

#cache_html
MAX_GET_ATTEMPTS = 15
TIMEOUT_SEC = 10

#product class
PAGE_PARAM = 'page={}'

#links.py
IO_PATH = Path.joinpath(ROOT_DIR, 'IOs')
LINK_SET_PATH = Path.joinpath(IO_PATH, 'link_set.json')
CACHED_FOLDER = Path.joinpath(ROOT_DIR, 'cached')
CACHE_DICT_PATH = Path.joinpath(IO_PATH, 'cache_dict.json')
SITECACHE_PATH = Path.joinpath(IO_PATH, 'sitecache.html')
DB_PATH = Path.joinpath(ROOT_DIR, 'my_db.sqlite')
# excel export
EXCEL_WB_PATH = lambda index: EXCEL_WB_PATH(index=index+1) if Path.exists(Path.joinpath(IO_PATH, f'market_dump{index}.xlsx')) else Path.joinpath(IO_PATH, f'market_dump{index}.xlsx')

#utils
# HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
class HEADERS(dict):
	_ua = None
	_HEADERS = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
			'Cache-Control': 'max-age=0',
			'Connection': 'keep-alive',
			'Cookie': 'yandexuid=3179560611566253940; yuidss=3179560611566253940; _ym_wasSynced=%7B%22time%22%3A1566262053967%2C%22params%22%3A%7B%22eu%22%3A0%7D%2C%22bkParams%22%3A%7B%7D%7D; _ym_uid=1566262054291930440; _ym_d=1566262054; mda=0; Session_id=3:1566262074.5.0.1566262074945:66f8bQ:1b.1|94495977.0.2|203879.874960.aIexdbn7uDm0ys4QhDGg7nV-bi4; sessionid2=3:1566262074.5.0.1566262074945:66f8bQ:1b.1|94495977.0.2|203879.942502.qErvb-YyX5wgxKnswZbLoJHFEPY; yp=1881613940.yrts.1566253940#1881613940.yrtsi.1566253940#1881622074.udn.cDpmb3J3ZWJjcmFw; L=XnsHR2lQc2BXVnp9Xm1cS3JAV3ZYQUsIIzU7HjNTBwtYAw==.1566262074.13963.311277.b383186ef7558369da91e3bd6ec9bff7; yandex_login=forwebcrap; i=LyfE9XTUEhlMFlTl2L40PdEKZ0X08Yf15Y9qbzE9Ad2rR3Q1aNsTpRB0XL7NofeN9hPpuZvA+Y0WBxs02Wgineg5/xY=; ys=svt.1; _ym_isad=1; _ym_visorc_784657=b; visits=1566345241-1566345241-1566345241; uid=AAAfaV1ciBmeVwDcEeqdAg==; js=1; novelty-badge-filter-payments=1566345241347; _ym_visorc_160656=b; _ym_visorc_45411513=b; first_visit_time=2019-08-21T02%3A54%3A05%2B03%3A00; fuid01=5d5c881b63f6b54c.hA5rOrGMyrakrdbZjbku11tSd3Keh4QQJXrepSqvQG-Jrmr8tNql45_T1laecTz8_Wrq2V9b0JJRJ2VzRPgwZFBLoxhyuGZydfiFddXsPxTaqqcv2SG1DQatS78jVYO1; yandexmarket=48; currentRegionId=213; currentRegionName=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D1%83; fonts-loaded=1; categoryQA=1; parent_reqid_seq=076188b8c58aa67a61163622b5d1abbd%2C04d296aaf076b96dc993112f4ffa72e8; HISTORY_AUTH_SESSION=19e2c543',
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
