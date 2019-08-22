import re

from common.models import ProductModel, Session

sess = Session()


q1 = sess.query(ProductModel).filter(ProductModel.name.ilike('%Crich с оливковым%')).first()
q2 = sess.query(ProductModel).filter(ProductModel.id == 156).first()



q3 = sess.query(ProductModel).filter(ProductModel.specs.ilike('%пше%')).limit(5).all()


q = sess.query(ProductModel).filter(ProductModel.other_shop == True).first()

q = sess.query(ProductModel).filter(ProductModel.detail_url == 'https://market.yandex.ru/product--pechene-schar-savoiardi-150-g/174208605/spec?show-uid=15663494825616024412116001&nid=73849&glfilter=16242946%3A16242947&context=search').first()
# q = sess.query(ProductModel).filter(ProductModel.img_url != None).first()
print(q)
print('q.list_url: ', q.list_url)
print('q.list_cache: ', q.list_cache)
print('q.detail_url: ', q.detail_url)
print('q.detail_cache: ', q.detail_cache)
print('q.img_url: ', q.img_url)


