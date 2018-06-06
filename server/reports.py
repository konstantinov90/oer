import os.path
from operator import itemgetter
import pymongo
import xlsxwriter

BASE_PATH = os.path.join(os.path.dirname(__file__), 'reports')

db = pymongo.MongoClient().inter_market

MGP_MATRIX = {
    'ARM': {
        'RUS-BLR': { 'src': 'RUS-ARM', 'mgps': ['BLR-ARM'] },
        'RUS-KAZ': { 'src': 'RUS-ARM', 'mgps': ['KAZ-ARM'] },
        'KAZ-KGZ': { 'src': 'RUS-ARM', 'mgps': ['KAZ-ARM', 'KGZ-RUS'] },
    },
    'BLR': {
        'RUS-ARM': { 'src': 'RUS-BLR', 'mgps': ['ARM-BLR'] },
        'RUS-KAZ': { 'src': 'RUS-BLR', 'mgps': ['KAZ-BLR'] },
        'KAZ-KGZ': { 'src': 'RUS-BLR', 'mgps': ['KAZ-BLR', 'KGZ-RUS'] },
    },
    'RUS': {
        'KAZ-KGZ': { 'src': 'RUS-KAZ', 'mgps': ['KGZ-RUS'] },
    },
    'KAZ': {
        'RUS-ARM': { 'src': 'RUS-KAZ', 'mgps': ['ARM-KAZ'] },
        'RUS-BLR': { 'src': 'RUS-KAZ', 'mgps': ['BLR-KAZ'] },
    },
    'KGZ': {
        'RUS-ARM': { 'src': 'KAZ-KGZ', 'mgps': ['ARM-KAZ', 'RUS-KGZ'] },
        'RUS-BLR': { 'src': 'KAZ-KGZ', 'mgps': ['BLR-KAZ', 'RUS-KGZ'] },
        'RUS-KAZ': { 'src': 'KAZ-KGZ', 'mgps': ['RUS-KGZ'] },
    },
}

COUNTRY_SECTION_NODE_MAP = {
    'sell': {
        'RUS': {
            'RUS-BLR': 'RUS1',
            'RUS-ARM': 'RUS2',
            'RUS-KAZ': 'RUS3',
        },
        'KAZ': {
            'RUS-KAZ': 'KAZ1',
            'KAZ-KGZ': 'KAZ2',
        },
        'ARM': { 'RUS-ARM': 'ARM1' },
        'BLR': { 'RUS-BLR': 'BLR1' },
        'KGZ': { 'KAZ-KGZ': 'KGZ1' },
    },
    'buy': {
        'RUS': {
            'RUS-BLR': 'BLR1',
            'RUS-ARM': 'ARM1',
            'RUS-KAZ': 'KAZ1',
            'KAZ-KGZ': 'KGZ1',
        },
        'KAZ': {
            'RUS-KAZ': 'RUS3',
            'KAZ-KGZ': 'KGZ1',
            'RUS-ARM': 'ARM1',
            'RUS-BLR': 'BLR1',
        },
        'ARM': {
            'RUS-ARM': 'RUS2',
            'RUS-BLR': 'BLR1',
            'RUS-KAZ': 'KAZ1',
            'KAZ-KGZ': 'KGZ1',
        },
        'BLR': {
            'RUS-BLR': 'RUS1',
            'RUS-ARM': 'ARM1',
            'RUS-KAZ': 'KAZ1',
            'KAZ-KGZ': 'KGZ1',
        },
        'KGZ': {
            'KAZ-KGZ': 'KAZ2',
            'RUS-BLR': 'BLR1',
            'RUS-ARM': 'ARM1',
            'RUS-KAZ': 'RUS3',
        },
    },
}

bid_getter = itemgetter('target_date', 'country_code', 'trader_code', 'dir')
section_getter = itemgetter('section_code', 'price', 'filled_volume')

def report_bids(session_id):
    bids = db.bids.find({'session_id': session_id})
    file_path = os.path.join(BASE_PATH, f'bids_session_{session_id}.xlsx')
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


sec_p_v_getter = itemgetter('filled_volume', 'node_price')

def report_user_bid(session_id, username):
    session = db.sessions.find_one({'_id': session_id})
    futures_session = db.sessions.find_one({'_id': session['futures_session_id']})
    sd_session = db.sessions.find_one({'_id': futures_session['sd_session_id']})

    bid = db.bids.find_one({'session_id': session_id, 'trader_code': username})
    rio = db.rio.find_one({'_id': username})
    spot_results = db.spot_results.find_one({'session_id': session_id})
    mgp_prices = {sec['section_code']: sec['mgp_price'] for sec in db.mgp_prices.find_one({'period_type': 'D', 'graph_type': 'FR', 'date_from': bid['target_date']})['sections']}
    sdd = list(db.sdd.find({'sessionId': sd_session['_id'], f'{rio["dir"]}er': username}))

    file_path = os.path.join(BASE_PATH, f'bid_{username}_{session_id}.xlsx')
    wb = xlsxwriter.Workbook(file_path, {'default_date_format': 'dd.mm.yyyy'})
    ws = wb.add_worksheet()
    # ws.write_row(0, 0, ['час', 'сумма дог', 'Объем', 'Цены', 'Результаты'])
    sections = rio['section_codes'] if rio['dir'] == 'sell' else ['RUS-ARM', 'RUS-BLR', 'RUS-KAZ', 'KAZ-KGZ']
    sec_len = len(sections)
    merge_format = wb.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1})
    bold_fmt = wb.add_format({'bold': True})
    cntr_fmt = wb.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
    date_fmt = wb.add_format({'align': 'center', 'num_format': 'dd.mm.yyyy'})
    brdr_fmt = wb.add_format({'border': 1, 'num_format': '# ##0'})

    ws.set_column('B:B', 22)
    ws.set_column('C:R', 10.4)

    ws.write(0, 0, f'Ценовая заявка на {"продажу" if rio["dir"] == "sell" else "покупку"} на рынке на сутки вперед', bold_fmt)
    ws.write(1, 0, 'Участник:', bold_fmt)
    ws.write(1, 1, rio['name'], cntr_fmt)
    ws.write(2, 0, 'Дата:', bold_fmt)
    ws.write(2, 1, bid['target_date'], date_fmt)
    ws.write(3, 0, 'Сессия №:', bold_fmt)
    ws.write(3, 1, session['_id'], cntr_fmt)

    ws.merge_range('A6:A8', 'час', merge_format)
    ws.merge_range('B6:B8', 'Суммарный объем, заключенных ранее договоров (СДД, срочные контракты)', merge_format)
    ws.merge_range('C6:C8', 'Объем, МВт·ч', merge_format)
    ws.merge_range(5, 3, 6, 3 + sec_len - 1, 'Цены, руб/МВт·ч', merge_format)
    ws.write_row(7, 3, sections, merge_format)
    ws.merge_range(5, 3 + sec_len, 5, 3 + sec_len * 3 + (1 if rio['dir'] == 'sell' else 2), 'Результаты', merge_format)
    for i, sec in enumerate(sections):
        ws.merge_range(6, 3 + sec_len + i * 2, 6, 4 + sec_len + i * 2, sec, merge_format)
        ws.write_row(7, 3 + sec_len + i * 2, ['Объем, МВт·ч', 'Цена, руб/МВт·ч'], merge_format)
    ws.merge_range(6, 3 + sec_len * 3, 7, 3 + sec_len * 3, 'Объем, МВт·ч', merge_format)
    ws.merge_range(6, 4 + sec_len * 3, 7, 4 + sec_len * 3, 'Стоимость, руб', merge_format)
    if rio['dir'] == 'buy':
        ws.merge_range(6, 5 + sec_len * 3, 7, 5 + sec_len * 3, 'Стоимость МГП, руб', merge_format)

    for hour, row in enumerate(range(8, 32)):
        [bid_hour] = [h['intervals'][0] for h in bid['hours'] if h['hour'] == hour]
        [spot_result] = [s['nodes'] for s in spot_results['hours'] if s['hour'] == hour]
        sum_sd = sum(h['accepted_volume'] for sd in sdd for h in sd['values'] if h['hour'] == hour and h['tdate'] == bid['target_date'])
        section_results = {sec: sec_pr for sec in sections for sec_pr in bid_hour['prices'] if sec_pr['section_code'] == sec}
        section_prices = [sec['price'] for sec in section_results.values()]
        for sec, sec_pr in section_results.items():
            [node_price] = [node['price'] for node in spot_result if node['code'] == COUNTRY_SECTION_NODE_MAP[rio['dir']][rio['country_code']][sec]]
            sec_pr['node_price'] = node_price
            if rio['dir'] == 'buy':
                if sec in MGP_MATRIX[rio['country_code']]:
                    sec_pr['mgp_price'] = 0
                    for mgp_sec in MGP_MATRIX[rio['country_code']][sec]['mgps']:
                        sec_pr['mgp_price'] += mgp_prices[mgp_sec]
        sec_res_p_v = [v for sec in section_results.values() for v in sec_p_v_getter(sec)]
        sum_res_v = sum(sec['filled_volume'] for sec in section_results.values())
        sum_res_am = sum(sec['filled_volume'] * sec['node_price'] for sec in section_results.values())
        if rio['dir'] == 'buy':
            sum_res_mgp = sum(sec['filled_volume'] * sec['mgp_price'] for sec in section_results.values() if 'mgp_price' in sec)
        ws.write_row(row, 0, [hour, sum_sd, bid_hour['volume']] + section_prices + sec_res_p_v + [sum_res_v, sum_res_am] + ([sum_res_mgp] if rio['dir'] == 'buy' else []), brdr_fmt)
    
    wb.close()
    return file_path

sd_getter = itemgetter('_id', 'author', 'section')
hr_getter = itemgetter('tdate', 'hour', 'volume', 'price', 'accepted_volume')
prt_getter = itemgetter('_id', 'name')

def report_user_sdd(session_id, username):
    session = db.sessions.find_one({'_id': session_id})
    rio = {row['_id']: row for row in db.rio.find()}
    query = {'sessionId': session_id}
    if username != 'admin':
        query[f'{rio[username]["dir"]}er'] = username
    sdd = db.sdd.find(query)

    file_path = os.path.join(BASE_PATH, f'sdd_{username}_{session_id}.xlsx')
    wb = xlsxwriter.Workbook(file_path, {'default_date_format': 'dd.mm.yyyy'})
    ws = wb.add_worksheet()

    bold_fmt = wb.add_format({'bold': True})
    big_bold_fmt = wb.add_format({'bold': True, 'font_size': 14})
    cntr_fmt = wb.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
    date_fmt = wb.add_format({'align': 'center', 'num_format': 'dd.mm.yyyy'})
    brdr_fmt = wb.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': False, 'border': 1, 'num_format': '# ##0'})
    hdr_fmt = wb.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1, 'bold': True})
    date_brdr_fmt = wb.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1, 'num_format': 'dd.mm.yyyy'})

    
    ws.set_column('A:A', 20)
    ws.set_column('B:B', 11)
    ws.set_column('C:C', 20)
    ws.set_column('D:D', 10)
    ws.set_column('E:E', 20)
    ws.set_column('F:H', 10)
    ws.set_column('I:I', 14)
    ws.set_column('J:J', 10)
    ws.set_column('K:K', 14)

    ws.write(0, 0, 'Отчет об исполнении свободных двусторонних договоров', big_bold_fmt)
    ws.write(1, 0, 'Участник:', bold_fmt)
    ws.write(1, 1, username if username == 'admin' else rio[username]['name'], cntr_fmt)
    ws.write(2, 0, 'Сессия №:', bold_fmt)
    ws.write(2, 1, session['_id'], cntr_fmt)
    ws.write(3, 0, 'Начало периода:', bold_fmt)
    ws.write(3, 1, session['startDate'], date_fmt)
    ws.write(4, 0, 'Окончание периода:', bold_fmt)
    ws.write(4, 1, session['finishDate'], date_fmt)

    ws.merge_range(6, 0, 7, 0, '№ договора', hdr_fmt)
    ws.merge_range(6, 1, 6, 2, 'Поставщик', hdr_fmt)
    ws.merge_range(6, 3, 6, 4, 'Покупатель', hdr_fmt)
    ws.write_row(7, 1, ['Код', 'Наименование', 'Код', 'Наименование'], hdr_fmt)
    ws.merge_range(6, 5, 7, 5, 'Сечение поставки', hdr_fmt)
    ws.merge_range(6, 6, 7, 6, 'Дата', hdr_fmt)
    ws.merge_range(6, 7, 7, 7, 'Час', hdr_fmt)
    ws.merge_range(6, 8, 7, 8, 'Заявленный объем, МВт·ч', hdr_fmt)
    ws.merge_range(6, 9, 7, 9, 'Цена, руб/МВт·ч', hdr_fmt)
    ws.merge_range(6, 10, 7, 10, 'Исполненный объем, МВт·ч', hdr_fmt)

    i = 8
    for sd in sdd:
        buyer = rio[sd['buyer']]
        seller = rio[sd['seller']]
        for hour in sd['values']:
            ws.write_row(i, 0, (sd['_id'],) + prt_getter(seller) + prt_getter(buyer) + (sd['section'],) +  hr_getter(hour), brdr_fmt)
            ws.write(i, 6, hour['tdate'], date_brdr_fmt)
            i += 1

    

    return file_path

def report_admin_bid(session_id, username):
    session = db.sessions.find_one({'_id': session_id})
    futures_session = db.sessions.find_one({'_id': session['futures_session_id']})
    sd_session = db.sessions.find_one({'_id': futures_session['sd_session_id']})

    file_path = os.path.join(BASE_PATH, f'bid_{username}_{session_id}.xlsx')
    wb = xlsxwriter.Workbook(file_path, {'default_date_format': 'dd.mm.yyyy'})
    ws = wb.add_worksheet()
    # ws.write_row(0, 0, ['час', 'сумма дог', 'Объем', 'Цены', 'Результаты'])
    sections = ['RUS-ARM', 'RUS-BLR', 'RUS-KAZ', 'KAZ-KGZ']
    sec_len = len(sections)
    merge_format = wb.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1})
    bold_fmt = wb.add_format({'bold': True})
    cntr_fmt = wb.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
    date_fmt = wb.add_format({'align': 'center', 'num_format': 'dd.mm.yyyy'})
    brdr_fmt = wb.add_format({'border': 1, 'num_format': '# ##0'})

    ws.set_column('B:B', 22)
    ws.set_column('C:R', 10.4)

    ws.write(0, 0, 'Ценовая заявка на рынке на сутки вперед', bold_fmt)
    ws.write(1, 0, 'Участник:', bold_fmt)
    ws.write(1, 1, 'Администратор', cntr_fmt)
    ws.write(2, 0, 'Дата:', bold_fmt)
    ws.write(2, 1, session['startDate'], date_fmt)
    ws.write(3, 0, 'Сессия №:', bold_fmt)
    ws.write(3, 1, session['_id'], cntr_fmt)

    ws.merge_range('A6:A8', 'час', merge_format)
    ws.merge_range('B6:B8', 'Суммарный объем, заключенных ранее договоров (СДД, срочные контракты)', merge_format)
    ws.merge_range('C6:C8', 'Объем, МВт·ч', merge_format)
    ws.merge_range(5, 3, 6, 3 + sec_len - 1, 'Цены, руб/МВт·ч', merge_format)
    ws.write_row(7, 3, sections, merge_format)
    ws.merge_range(5, 3 + sec_len, 5, 3 + sec_len * 3 + 2, 'Результаты', merge_format)


    for i, sec in enumerate(sections):
        ws.merge_range(6, 3 + sec_len + i * 2, 6, 4 + sec_len + i * 2, sec, merge_format)
        ws.write_row(7, 3 + sec_len + i * 2, ['Объем, МВт·ч', 'Цена, руб/МВт·ч'], merge_format)
    ws.merge_range(6, 3 + sec_len * 3, 7, 3 + sec_len * 3, 'Объем, МВт·ч', merge_format)
    ws.merge_range(6, 4 + sec_len * 3, 7, 4 + sec_len * 3, 'Стоимость, руб', merge_format)
    ws.merge_range(6, 5 + sec_len * 3, 7, 5 + sec_len * 3, 'Стоимость МГП, руб', merge_format)

    spot_results = db.spot_results.find_one({'session_id': session_id})
    mgp_prices = {sec['section_code']: sec['mgp_price'] for sec in db.mgp_prices.find_one({'period_type': 'D', 'graph_type': 'FR', 'date_from': session['startDate']})['sections']}

    row = 8
    for rio in db.rio.find():
        bid = db.bids.find_one({'session_id': session_id, 'trader_code': rio['_id']})
        if not bid:
            continue
        sdd = list(db.sdd.find({'sessionId': sd_session['_id'], f'{rio["dir"]}er': rio['_id']}))

        for hour in range(24):
            [bid_hour] = [h['intervals'][0] for h in bid['hours'] if h['hour'] == hour]
            [spot_result] = [s['nodes'] for s in spot_results['hours'] if s['hour'] == hour]
            sum_sd = sum(h['accepted_volume'] for sd in sdd for h in sd['values'] if h['hour'] == hour and h['tdate'] == bid['target_date'])
            section_results = {sec: sec_pr for sec in sections for sec_pr in bid_hour['prices'] if sec_pr['section_code'] == sec}
            section_prices = [section_results.get('price', '') for sec in sections]
            for sec in sections: # section_results.items():
                sec_pr = section_results.get(sec, {})
                try:
                    [node_price] = [node['price'] for node in spot_result if node['code'] == COUNTRY_SECTION_NODE_MAP[rio['dir']][rio['country_code']].get(sec)]
                except:
                    node_price = ''
                sec_pr['node_price'] = node_price
                if rio['dir'] == 'buy':
                    if sec in MGP_MATRIX[rio['country_code']]:
                        sec_pr['mgp_price'] = 0
                        for mgp_sec in MGP_MATRIX[rio['country_code']][sec]['mgps']:
                            sec_pr['mgp_price'] += mgp_prices[mgp_sec]
            sec_res_p_v = [v for sec in sections for v in (sec_pr.get('filled_volume'), sec_pr.get('node_price'))]
            sum_res_v = sum(sec['filled_volume'] for sec in section_results.values())
            sum_res_am = sum(sec['filled_volume'] * sec['node_price'] for sec in section_results.values())
            if rio['dir'] == 'buy':
                sum_res_mgp = sum(sec['filled_volume'] * sec['mgp_price'] for sec in section_results.values() if 'mgp_price' in sec)
            ws.write_row(row, 0, [hour, sum_sd, bid_hour['volume']] + section_prices + sec_res_p_v + [sum_res_v, sum_res_am] + ([sum_res_mgp] if rio['dir'] == 'buy' else []), brdr_fmt)

        row += 1
    
    wb.close()
    return file_path
