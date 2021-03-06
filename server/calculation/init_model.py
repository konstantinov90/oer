import os.path
import xlrd
import pymongo

from .model_file_loader import ModelFileLoader

BASE_PATH = os.path.join(os.path.dirname(__file__), 'model')

db = pymongo.MongoClient().inter_market

COL_NAME, COL_DIRECTION, COL_CODE, COL_PWD, COL_COUNTRY = 2, 3, 4, 5, 9

SECTION_CODES = {
    'ARM': ['RUS-ARM'],
    'BLR': ['RUS-BLR'],
    'RUS': ['RUS-ARM', 'RUS-BLR', 'RUS-KAZ'],
    'KAZ': ['RUS-KAZ', 'KAZ-KGZ'],
    'KGZ': ['KAZ-KGZ'],
}

def upload_users():
    wb = xlrd.open_workbook(os.path.join(BASE_PATH, 'out_Final.xls'))
    data = wb.sheet_by_index(0)._cell_values

    users = [{'_id': 'admin', 'password': 'admin'}]
    rio = []

    for row in data[1:]:
        users.append({
            '_id': row[COL_CODE],
            'password': str(int(row[COL_PWD])),
        })

        rio.append({
            '_id': row[COL_CODE],
            'country_code': row[COL_COUNTRY],
            'login': row[COL_CODE],
            'dir': 'sell' if row[COL_DIRECTION] == 'ПОСТАВЩИК' else 'buy',
            'name': row[COL_NAME],
            'section_codes': SECTION_CODES[row[COL_COUNTRY]],
        })
    
    db.users.delete_many({})
    db.rio.delete_many({})
    db.users.insert_many(users)
    db.rio.insert_many(rio)

def upload_mgp_prices():
    data = ModelFileLoader.parse_mgp_prices(os.path.join(BASE_PATH, 'МГП_биржа_рсв.XLSX'))
    db.mgp_prices.remove({})
    db.mgp_prices.insert_many(data)
