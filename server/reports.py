import os.path
from operator import itemgetter
import pymongo
import xlsxwriter

BASE_PATH = os.path.join(os.path.dirname(__file__), 'reports')

db = pymongo.MongoClient().inter_market

bid_getter = itemgetter('target_date', 'country_code', 'trader_code', 'dir')
section_getter = itemgetter('section_code', 'price', 'filled_volume')

def report_bids(session_id):
    bids = db.bids.find({'session_id': session_id})
    file_path = os.path.join(f'bids_session_{session_id}.xlsx')
    wb = xlsxwriter.Workbook(file_path, {'default_date_format': 'dd-mm-yyyy'})
    ws = wb.add_worksheet()
    ws.set_column('A:A', 10)
    ws.set_column('C:C', 10)
    ws.write_row(0, 0, ['дата', 'страна', 'код участника', 'направление', 'час', 'объем заявки', 'сечение', 'цена', 'принятый объем'])
    i = 1
    for bid in bids:
        for hour in bid['hours']:
            for section in hour['intervals'][0]['prices']:
                ws.write_row(i, 0, bid_getter(bid) + (hour['hour'], hour['intervals'][0]['volume']) + section_getter(section))
                i += 1
    return file_path
