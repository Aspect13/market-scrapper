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
			'Content-Type': 'text/html; charset=utf-8',
			'Cache-Control': 'max-age=0',
			'Connection': 'keep-alive',
			'Cookie': 'yandexuid=3179560611566253940; yuidss=3179560611566253940; _ym_uid=1566262054291930440; _ym_d=1566262054; mda=0; novelty-badge-filter-payments=1566345241347; fuid01=5d5c881b63f6b54c.hA5rOrGMyrakrdbZjbku11tSd3Keh4QQJXrepSqvQG-Jrmr8tNql45_T1laecTz8_Wrq2V9b0JJRJ2VzRPgwZFBLoxhyuGZydfiFddXsPxTaqqcv2SG1DQatS78jVYO1; currentRegionId=213; currentRegionName=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D1%83; categoryQA=1; yp=1881613940.yrts.1566253940#1881613940.yrtsi.1566253940#1881711250.udn.cDppbnNlbnNlLWluc2lnaHRz#1881711250.multib.1; L=QEBVVFxlR08GbGQBUlJpBF56ZF4DX1JAIVZHDiQgMEIMNx4wCB9EBQ==.1566351250.13964.372283.7f3f7a8ea43e767579b294465f5261fa; yandex_login=insense-insights; i=HgaZ81BVS3LsyHmhUpQ+VeL018I7Dt9EzcRh7r3g75QOaHq0+3LOSGHiQYrTAcOQ7EqRVlpuwiboLAKi69QTA53Xwxk=; sber-bonus-popup-viewed=1; Session_id=3:1567022383.5.1.1566262074945:66f8bQ:1b.1|94495977.0.2|870775430.89176.2.2:89176|204301.254396.PUJli4Pi7ZylsJCdio5vU_YFJPI; sessionid2=3:1567022383.5.0.1566262074945:66f8bQ:1b.1|94495977.0.2|870775430.-1.0|204301.630253.HqTJFsrJMxtQD2eZnb5Y1nmt0Es; instruction=1; specific=1; ys=svt.1; visits=1566345241-1566477068-1567185843; uid=AABcEl1pW7MKBRU0A5j1Ag==; js=1; first_visit_time=2019-08-30T20%3A24%3A06%2B03%3A00; _ym_visorc_160656=b; fonts-loaded=1; _ym_isad=1; _ym_visorc_45411513=b; parent_reqid_seq=9fc05dea71930d94ae80e650dac7841b%2Cb46ea219d8f65e578e0a28d5713fa9bc%2C5cfa37137850fb6c1509af578c95516a%2Cc00f94101198ad35be8e80757b644f37%2Cc385b350eae08bf8c0abfbe5841c43b7; HISTORY_AUTH_SESSION=779d60c; oChC=2',

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
