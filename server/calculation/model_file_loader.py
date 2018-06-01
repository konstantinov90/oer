import functools
import json
import os.path
from xml.etree import ElementTree
from datetime import datetime

import xlrd


model_path_resolver = functools.partial(os.path.join, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model'))

class ModelFileLoader():
    @staticmethod
    def parse_generic_json(filename):
        with open(filename, 'r', encoding='utf-8') as fd:
            return json.load(fd)

    @classmethod
    def load_countries(cls):
        return cls.parse_generic_json(model_path_resolver('countries.json'))

    @classmethod
    def load_nodes(cls):
        return cls.parse_generic_json(model_path_resolver('nodes.json'))

    @classmethod
    def load_sections(cls):
        return cls.parse_generic_json(model_path_resolver('sections.json'))

    @classmethod
    def load_participants(cls):
        return cls.parse_generic_json(model_path_resolver('participants.json'))

    SECTION_LIMITS_DATA = None
    @classmethod
    def parse_section_limits(cls, filename, limit_type='SECTION_FLOW_LIMIT_FC'):
        if cls.SECTION_LIMITS_DATA:
            return cls.SECTION_LIMITS_DATA

        tree = ElementTree.parse(filename)
        assert tree.getroot().attrib['class'] == limit_type

        res = {}
        for row in tree.iter('row'):
            d = datetime.strptime(row.attrib['target-day'], '%Y%m%d')
            day = res.setdefault(d, {'target_date': d, 'limit_type': limit_type, 'hours': {}})
            hour = day['hours'].setdefault(row.attrib['target-hour'], {'hour': int(row.attrib['target-hour']), 'sections': {}})

            section = hour['sections'].setdefault(row.attrib['section-code'], {'section_code': row.attrib['section-code']})
            
            section_code = '{}-{}'.format(row.attrib['country-code-from'], row.attrib['country-code-to'])

            if section_code == row.attrib['section-code']:
                section['pmax_fw'] = float(row.attrib['flow-limit'])
                if 'extra-limit-ex' in row.attrib:
                    section['extra_limit_ex_fw'] = float(row.attrib['extra-limit-ex'])
                    section['extra_limit_dam_fw'] = float(row.attrib['extra-limit-dam'])
            else:
                section['pmax_bw'] = float(row.attrib['flow-limit'])
                if 'extra-limit-ex' in row.attrib:
                    section['extra_limit_ex_bw'] = float(row.attrib['extra-limit-ex'])
                    section['extra_limit_dam_bw'] = float(row.attrib['extra-limit-dam'])


        for day in res.values():
            day['hours'] = list(day['hours'].values())
            for hour in day['hours']:
                hour['sections'] = list(hour['sections'].values())
        
        cls.SECTION_LIMITS_DATA = list(res.values())
        return cls.SECTION_LIMITS_DATA


    @classmethod
    def parse_section_limits_excel(cls, filename, limit_type='SECTION_FLOW_LIMIT_FC'):
        if cls.SECTION_LIMITS_DATA:
            return cls.SECTION_LIMITS_DATA

        COL_DATE, COL_HOUR, COL_FROM_CODE, COL_TO_CODE, COL_SECTION, COL_PMAX = range(6)

        wb = xlrd.open_workbook(filename)
        data = wb.sheet_by_index(0)._cell_values

        res = {}

        for row in data[1:]:
            d = xlrd.xldate.xldate_as_datetime(row[COL_DATE], 0)
            day = res.setdefault(d, {'target_date': d, 'hours': {}})
            hour = day['hours'].setdefault(row[COL_HOUR], {'hour': int(row[COL_HOUR]), 'sections': {}})

            section = hour['sections'].setdefault(row[COL_SECTION], {'section_code': row[COL_SECTION]})
            
            section_code = '{}-{}'.format(row[COL_FROM_CODE], row[COL_TO_CODE])

            if section_code == row[COL_SECTION]:
                section['pmax_fw'] = float(row[COL_PMAX])
            else:
                section['pmax_bw'] = float(row[COL_PMAX])

        for day in res.values():
            day['hours'] = list(day['hours'].values())
            day['limit_type'] = limit_type
            for hour in day['hours']:
                hour['sections'] = list(hour['sections'].values())
        
        cls.SECTION_LIMITS_DATA = list(res.values())
        return cls.SECTION_LIMITS_DATA

    @classmethod
    def load_section_limits(cls, target_date, hour, limit_type='SECTION_FLOW_LIMIT_FC', session_id='Не используется'):
        data = cls.parse_section_limits(model_path_resolver('Section_limits_FC.xml'), limit_type)
        [day] = [row for row in data if row['target_date'] == target_date]
        [hour] = [row for row in day['hours'] if row['hour'] == hour]
        return hour['sections']

    MGP_DATA = None
    @classmethod
    def parse_mgp_prices(cls, file_name):
        if cls.MGP_DATA:
            return cls.MGP_DATA

        COL_FROM_CODE, COL_TO_CODE, _, COL_PERIOD_TYPE, COL_GRAPH_TYPE, COL_PRICE, COL_DATE_FROM, COL_DATE_TO = range(8)

        wb = xlrd.open_workbook(file_name)
        data = wb.sheet_by_index(0)._cell_values

        res = {}

        for row in data[1:]:
            d_from = xlrd.xldate.xldate_as_datetime(row[COL_DATE_FROM], 0)
            d_to = xlrd.xldate.xldate_as_datetime(row[COL_DATE_TO], 0)
            period, graph_type = row[COL_PERIOD_TYPE], row[COL_GRAPH_TYPE]
            unit = res.setdefault((d_from, d_to, period, graph_type), {
                'date_from': d_from,
                'date_to': d_to,
                'period_type': period,
                'graph_type': graph_type,
                'sections': [],
            })
            unit['sections'].append({'section_code': '{}-{}'.format(row[COL_FROM_CODE], row[COL_TO_CODE]),
                                     'mgp_price': float(row[COL_PRICE])})

        cls.MGP_DATA = list(res.values())
        return cls.MGP_DATA

    @classmethod
    def load_mgp_prices(cls, target_date, hour):
        data = cls.parse_mgp_prices(model_path_resolver('МГП_биржа_рсв.XLSX'))
        [day] = [row for row in data
                 if row['date_from'] == target_date and row['period_type'] == 'D' and row['graph_type'] == 'FR']
        return day['sections']

if __name__ == '__main__':
    import datetime
    data = ModelFileLoader.load_section_limits(datetime.datetime(2018,6,18), 11)
    # data = ModelFileLoader.load_mgp_prices(datetime.datetime(2018,6,23), 8)
    # data = ModelFileLoader.load_sections()
