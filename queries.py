import re

from common.models import ProductModel, Session

sess = Session()


q1 = sess.query(ProductModel).filter(ProductModel.name.ilike('%Crich с оливковым%')).first()
q1 = sess.query(ProductModel).filter(ProductModel.id == 156).first()

print(q1)
print(q1.list_url)
print(q1.list_cache)
print(q1.detail_url)
print(q1.detail_cache)


q2 = sess.query(ProductModel).filter(ProductModel.specs.ilike('%пше%')).limit(5).all()
from sqlalchemy import or_

conditions = []
for name in ['пшен', 'полб']:
    conditions.append(ProductModel.specs.ilike(f'%{name}%'))

q3 = sess.query(ProductModel).filter(
    ~or_(*conditions)
)

patt = re.compile(r' (\d+) г', re.UNICODE)
for i in q3:
	print(i.name)
	x = re.findall(patt, i.name)
	try:
		print(int(x[0]))
	except IndexError:
		print(None)
