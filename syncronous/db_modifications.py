from sqlalchemy import and_

from common.models import ProductModel, Session
from syncronous.utils import get_true_other_shop_url


def resolve_all_other_shop_urls(session):
	for product in session.query(ProductModel).filter(
			and_(ProductModel.other_shop, ProductModel.other_shop_url == None)
	).all():

		product.other_shop_url = get_true_other_shop_url(product.detail_url)
		session.add(product)

	session.commit()


if __name__ == '__main__':
	session = Session()
	resolve_all_other_shop_urls(session)
