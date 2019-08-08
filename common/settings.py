from fake_useragent import UserAgent

#cache_html
MAX_GET_ATTEMPTS = 15
TIMEOUT_SEC = 10

#product class
PAGE_PARAM = 'page={}'

#links.py
LINK_SET_PATH = 'IOs/link_set.json'
CACHED_FOLDER = 'cached'
CACHE_DICT_PATH = 'IOs/cache_dict.json'
SITECACHE_PATH = 'IOs/sitecache.html'

#utils
ua = UserAgent()
# HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
_HEADERS = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
		'Cache-Control': 'max-age=0',
		'Connection': 'keep-alive',
		'Cookie': 'yandexuid=66768161542820144; _ym_uid=15470668491035248607; mda=0; my=YwA=; L=Vg5qWlJTaEYEUXdRaHBISWwGUkZAfllaLAFBUD1GNmUsIjsmHgkxQw==.1560425001.13895.32511.6d7f0800b84fe5ad8d9fb58a5470ff12; yandex_login=insense-insights; i=sqYepcpOgHj3FDLbSa6q/BOs6rkpYwQ/tA1QnMbUgc1OMRAtZNG5RC0Y0pfmJvL2RosYkV/eoXvnww+MXGT8r5LvetM=; currentRegionId=213; fuid01=5d25fc545a682083.0ijTUSuGThKRwW24tcNbJrbVzjyIKyxS0i52QOUbGcKISAB5DXX9onryQ-cOflBE2eXdVhJjtfn1F8bAPCChVKp1kl6aK2CEx1p9XJe9J_C5AxIEtAQHUUvq5rjZi4Jd; currentRegionName=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D1%83; yp=1574394535.szm.1:1600x900:1600x770#1875785001.udn.cDppbnNlbnNlLWluc2lnaHRz#1595500845.yrts.1563964845#1858180170.yrtsi.1542820170#1567252407.ygu.1; yandex_gid=213; bltsr=1; EIXtkCTlX=1; yabs-frequency=/4/0000000000000000/vezoSAms8Hg-FMsiDYS0/; zm=m-white_bender.webp.css-https%3As3home-static_hUP0kziUfLzpe0NLvqqXcbftIqc%3Ac; Session_id=3:1565105496.5.0.1560425001001:5y0nLg:20.1|870775430.0.2|203237.267840.h8ayKMxsGF51T-9e5Ppe-mwFZYA; sessionid2=3:1565105496.5.0.1560425001001:5y0nLg:20.1|870775430.0.2|203237.954346.lq_MeZB4VzQsnMpsXwS-aY6Oq_w; _ym_uid=15470668491035248607; _ym_d=1565105499; sber-bonus-popup-viewed=1; novelty-badge-filter-payments=-1; categoryQA=1; oChC=1; oChD=1; ys=svt.1; uid=AABbhl1MaMG0DABMBgtuAg==; first_visit_time=2019-08-08T21%3A24%3A02%2B03%3A00; fonts-loaded=1; _ym_isad=1; js=1; yandexmarket=48; visits=1562770513-1565213501-1565298126; parent_reqid_seq=57c0926830a7dcbee7f1d0897a0d2bf8%2C569a0c487aa922c0de8d57b566943732%2C3cbb7dc658f7357632677ba6e5730697%2C1e9c8a328e11cb31076d1179037cccbc%2C1445894cf2761f831eaf8c197cb340e4; HISTORY_AUTH_SESSION=1c7b228; _ym_visorc_160656=b; _ym_visorc_45411513=b',
		# 'DNT': '1',
		# 'Host': 'market.yandex.ru',
		# 'Sec-Fetch-Mode': 'navigate',
		# 'Sec-Fetch-Site': 'none',
		# 'Sec-Fetch-User': '?1',
		# 'Upgrade-Insecure-Requests': '1',
	}


def HEADERS():
	_HEADERS.update({'User-Agent': ua.random})
	return _HEADERS


# excel export
EXCEL_WB_PATH = '../IOs/market_dump.xlsx'
