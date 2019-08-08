from common.models import Session, ProductModel, ReviewModel
from common.settings import EXCEL_WB_PATH
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
	wb.save(EXCEL_WB_PATH)


if __name__ == '__main__':
	session = Session()
	dump_to_excel(session)