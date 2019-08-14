import datetime
import json
from pathlib import Path

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from common.misc import pathify
from settings import DB_PATH, LINK_SET_PATH, CACHE_DICT_PATH, CACHED_FOLDER

engine = create_engine(f'sqlite:///{DB_PATH}', echo=__name__ == '__main__')
Session = sessionmaker(bind=engine)
Base = declarative_base()


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

	@property
	def list_url(self):
		link_set = json.load(open(LINK_SET_PATH, 'r', encoding='utf8'))
		x = filter(lambda i: i['category_name'] == self.category_description, link_set)
		return list(x)[0]['url']

	@property
	def list_cache(self):
		return self.get_cache_path(self.list_url)

	@property
	def detail_cache(self):
		return self.get_cache_path(self.detail_url)

	@staticmethod
	@pathify(CACHED_FOLDER)
	def get_cache_path(url):
		cache_dict = json.load(open(CACHE_DICT_PATH, 'r'))
		return cache_dict.get(url, 'NO CACHE FOR THIS URL')

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
		return '<ReviewModel id={id} date={date} product={product_id}>'.format(**self.__dict__, id=self.id, product_id=self.product_id)





if __name__ == '__main__':
	@pathify(CACHED_FOLDER)
	def tst(qqq='123'):
		print('inside', qqq)
		return ProductModel.get_cache_path(qqq)
	# Base.metadata.create_all(engine)
	x = tst()
	print(x)

