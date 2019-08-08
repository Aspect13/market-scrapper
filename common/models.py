import datetime

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///../my_db.sqlite', echo=__name__ == '__main__')
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
	Base.metadata.create_all(engine)
