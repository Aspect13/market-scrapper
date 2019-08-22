import datetime
import json
import re
from pathlib import Path

from pip._internal.utils.misc import cached_property
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from common.misc import pathify, get_cache_dict, get_link_set
from settings import DB_PATH, LINK_SET_PATH, CACHE_DICT_PATH, CACHED_FOLDER

engine = create_engine(f'sqlite:///{DB_PATH}', echo=__name__ == '__main__')
Session = sessionmaker(bind=engine)
Base = declarative_base()


WEIGHT_PATTERN = re.compile(r' (\d+) г', re.UNICODE)


class ProductModel(Base):
	__tablename__ = 'products'

	id = Column(Integer, primary_key=True)
	date_added = Column(DateTime, default=datetime.datetime.now)

	category_description = Column(String(256), nullable=True)
	yandex_id = Column(Integer, unique=True, nullable=True)

	name = Column(String(128), nullable=False)
	detail_url = Column(String(512), nullable=False, unique=True)
	original_price = Column(Integer, nullable=True)
	final_price = Column(Integer, nullable=True)
	specs = Column(String(1024), nullable=True)
	reviews = relationship('ReviewModel', back_populates='product')

	other_shop = Column(Boolean, default=False, nullable=False)
	other_shop_id = Column(String(128), nullable=True)
	other_shop_url = Column(String(512), nullable=True, unique=True)

	img_url = Column(String(256), nullable=False,)
	img_local_path = Column(String(256), nullable=True)

	@property
	def list_url(self):
		link_set = get_link_set()
		x = filter(lambda i: i['category_name'] == self.category_description, link_set)
		return next(x, {}).get('url')

	@property
	def list_cache(self):
		return self.get_cache_path(self.list_url)

	@property
	def detail_cache(self):
		return self.get_cache_path(self.detail_url)

	@staticmethod
	@pathify(CACHED_FOLDER)
	def get_cache_path(url):
		cache_dict = get_cache_dict()
		return cache_dict.get(url, 'NO CACHE FOR THIS URL')

	@staticmethod
	def get_weight_from_name(name):
		m = re.findall(WEIGHT_PATTERN, name)
		try:
			return int(m[0])
		except IndexError:
			return

	@cached_property
	def weight(self):
		return self.get_weight_from_name(self.name)

	@property
	def price_for_100_original(self):
		if self.weight:
			return int(self.original_price) / self.weight * 100
		return

	@property
	def price_for_100_final(self):
		if self.weight:
			return int(self.final_price) / self.weight * 100
		return

	def __repr__(self):
		return '<ProductModel id={id} name={name}>'.format(id=self.id, name=self.name)


class ReviewModel(Base):
	__tablename__ = 'reviews'

	id = Column(Integer, primary_key=True)
	yandex_id = Column(Integer, nullable=True)
	author = Column(String(128), nullable=False)
	rating = Column(Integer, nullable=False)
	pros = Column(String(512), nullable=True)
	cons = Column(String(512), nullable=True)
	comment = Column(String(512), nullable=True)
	date = Column(Date, )
	product_id = Column(Integer, ForeignKey('products.id'))
	product = relationship('ProductModel', back_populates='reviews')

	def __repr__(self):
		return '<ReviewModel id={id} date={date} product={product_id}>'.format(
			**self.__dict__, id=self.id, product_id=self.product_id
		)


class CachedHtml(Base):
	__tablename__ = 'cached_html'

	id = Column(Integer, primary_key=True)

	url = Column(String(512), nullable=False, unique=True)
	file_name = Column(String(128), nullable=False, unique=True)
	date_added = Column(DateTime, default=datetime.datetime.now)

	def __repr__(self):
		return '<CachedHtml id={id} date={date} file_name={file_name} url={url}>'.format(
			**self.__dict__, id=self.id
		)


if __name__ == '__main__':
	Base.metadata.create_all(engine)

