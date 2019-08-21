from sqlalchemy import or_

from common.models import Session, ProductModel, ReviewModel
from settings import EXCEL_WB_PATH
from openpyxl import Workbook, styles


def write_model_to_worksheet(wb, model, session):
	ws = wb.create_sheet(model.__tablename__)
	ws.append(model.__table__.columns.keys())
	for product in session.query(model).all():
		data = list(map(product.__dict__.get, model.__table__.columns.keys()))
		ws.append(data)


def write_model_to_worksheet_all(wb, model, session):
	ws = wb.create_sheet(model.__tablename__)
	header = model.__table__.columns.keys()
	header += ['weight', 'price_for_100_original', 'price_for_100_final']
	ws.append(header)
	for product in session.query(model).all():
		data = list(map(product.__dict__.get, model.__table__.columns.keys()))
		data += [product.weight, product.price_for_100_original, product.price_for_100_final]
		ws.append(data)


def write_model_to_worksheet_filtered(wb, model, session):
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


def write_model_to_worksheet_highlight(wb, model, session):
	red_col = styles.colors.Color(rgb='00FF0000')
	red_fill = styles.fills.PatternFill(patternType='solid', fgColor=red_col)
	ws = wb.create_sheet(model.__tablename__)
	header = model.__table__.columns.keys()
	header += ['weight', 'price_for_100_original', 'price_for_100_final']
	ws.append(header)
	for product in session.query(model).all():
		data = list(map(product.__dict__.get, model.__table__.columns.keys()))
		data += [product.weight, product.price_for_100_original, product.price_for_100_final]
		ws.append(data)
		specs = product.specs or ''
		if any(i in specs for i in ['пшен', 'полб', 'рожь', 'ячме']):
			ws.row_dimensions[ws._current_row].fill = red_fill


def dump_to_excel(session, func, suffix='', write_only=True):
	wb = Workbook(write_only=write_only)
	func(wb, ProductModel, session)
	write_model_to_worksheet(wb, ReviewModel, session)
	wb.save(EXCEL_WB_PATH(suffix))


if __name__ == '__main__':
	session = Session()
	dump_to_excel(session, write_model_to_worksheet_all, '_all')
	dump_to_excel(session, write_model_to_worksheet_filtered, '_filtered')
	dump_to_excel(session, write_model_to_worksheet_highlight, '_highlight', write_only=False)
