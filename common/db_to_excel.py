import re

from sqlalchemy import or_

from common.models import Session, ProductModel, ReviewModel
from settings import EXCEL_WB_PATH
from openpyxl import Workbook


def write_model_to_worksheet(wb, model, session):
	ws = wb.create_sheet(model.__tablename__)
	ws.append(model.__table__.columns.keys())
	for row in session.query(model).all():
		ws.append(list(map(row.__dict__.get, model.__table__.columns.keys())))


def dump_to_excel(session):
	wb = Workbook(write_only=True)
	write_model_to_worksheet(wb, ProductModel, session)
	write_model_to_worksheet(wb, ReviewModel, session)
	wb.save(EXCEL_WB_PATH(0))


def dump_to_excel2(session):
	wb = Workbook(write_only=True)
	write_model_to_worksheet_filtered_price_for_100(wb, ProductModel, session)
	write_model_to_worksheet_filtered_price_for_100(wb, ReviewModel, session)
	wb.save(EXCEL_WB_PATH(0))


def write_model_to_worksheet_filtered_price_for_100(wb, model, session):
	ws = wb.create_sheet(model.__tablename__)
	header = model.__table__.columns.keys()
	header += ['weight', 'price_for_100_original', 'price_for_100_final']
	ws.append(header)
	conditions = []
	for name in ['пшен', 'полб', 'рожь', 'ячме']:
		conditions.append(ProductModel.specs.ilike(f'%{name}%'))

	q = session.query(ProductModel).filter(
		~or_(*conditions)
	)

	for product in q.all():
		data = list(map(product.__dict__.get, model.__table__.columns.keys()))
		data += [product.weight, product.price_for_100_original, product.price_for_100_final]
		ws.append(data)


if __name__ == '__main__':
	session = Session()
	dump_to_excel2(session)
	dump_to_excel(session)
