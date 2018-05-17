import pymongo
import xlrd

DB = pymongo.MongoClient().inter_market

COL_DATE = 0
COL_HOUR = 1
COL_SECTION = 2
COL_PMAX = 3
COL_PMIN = 4

COL_COUNTRY_FROM = 2
COL_COUNTRY_TO = 3
COL_MGP_PRICE = 4

def load_section_limits(file_name):
    wb = xlrd.open_workbook(file_name)
    data = wb.sheet_by_index(0)._cell_values

    doc_data = {}

    for row in data[1:]:
        d = xlrd.xldate.xldate_as_datetime(row[COL_DATE], 0)

        date_doc = doc_data.setdefault(d, {'tdate': d, 'hours': [{}] * 24})

        h = int(row[COL_HOUR])

        hour_doc = date_doc['hours']

        hour_doc[h][row[COL_SECTION]] = {'pmax_fw': float(row[COL_PMAX]), 'pmax_bw': float(row[COL_PMIN])}

    DB.section_limits.delete_many({})
    DB.section_limits.insert_many([doc for doc in doc_data.values()])

def load_mgp_prices(file_name):
    wb = xlrd.open_workbook(file_name)
    data = wb.sheet_by_index(0)._cell_values

    doc_data = {}

    for row in data[1:]:
        d = xlrd.xldate.xldate_as_datetime(row[COL_DATE], 0)
        date_doc = doc_data.setdefault(d, {'tdate': d, 'hours': [{}] * 24})

        h = int(row[COL_HOUR])

        hour_doc = date_doc['hours']

        hour_doc[h][f'{row[COL_COUNTRY_FROM]}-{row[COL_COUNTRY_TO]}'] = float(row[COL_MGP_PRICE])

    DB.mgp_prices.delete_many({})
    DB.mgp_prices.insert_many([doc for doc in doc_data.values()])


if __name__ == '__main__':
    load_section_limits(r'E:\git\InterMarketDemo\calculation\model\section_limits.xlsx')
    load_mgp_prices(r'E:\git\InterMarketDemo\calculation\model\mgp_prices.xlsx')
