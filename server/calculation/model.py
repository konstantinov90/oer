from pyomo.environ import *
from pyomo.opt import SolverStatus, TerminationCondition
import json
import xlrd
import os
import os.path


SOLVER = 'cplex'
SOLVER_PATH = r'C:\Program Files\IBM\ILOG\CPLEX_Enterprise_Server1261\CPLEX_Studio\cplex\bin\x64_win64\cplex.exe'
# SOLVER = 'glpk'
# SOLVER_PATH = r'C:\Program Files\winglpk\w64\glpsol.exe'
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
DIR = {'buy': 1, 'sell': -1}


COL_DATE = 0
COL_HOUR = 1
COL_SECTION = 2
COL_PMAX = 3
COL_PMIN = 4

COL_COUNTRY_FROM = 2
COL_COUNTRY_TO = 3
COL_MGP_PRICE = 4

# TODO отсекание заявок на уровне узла - все что явно не может быть удовлетворено выкидываем


class Section:
    def __init__(self, node_from, node_to, cut_countries, distr_rule):
        self.node_from = node_from
        self.node_to = node_to
        self.pmax_fw = None
        self.pmax_bw = None
        self.flow = None
        self.price = None
        self.cut_countries = cut_countries
        self.distr_rule = distr_rule

    def __str__(self):
        return self.code + ': ' + self.name
        
    @property
    def code(self):
        return self.node_from.country.code + '-' + self.node_to.country.code
    
    @property
    def name(self):
        return self.node_from.country.name + ' - ' + self.node_to.country.name

    def __lt__(self, other):
        return self.code < other.code

    def flow_dir(self, from_country, to_country):
        if to_country in self.cut_countries and from_country not in self.cut_countries:
            return 1
        elif to_country not in self.cut_countries and from_country in self.cut_countries:
            return -1
        else:
            return 0

    def calc_flow(self, model, objects):
         return sum(model.x[obj].value * self.flow_dir(*obj.country_from_to()) for obj in objects)


class Country:
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def __str__(self):
        return self.code + ': ' + self.name


class Node:
    def __init__(self, code, name, country):
        self.code = code
        self.name = name
        self.country = country
        self.price = None

    def __str__(self):
        return self.code + ': ' + self.name

    def __lt__(self, other):
        return self.code < other.code


class Participant:
    def __init__(self, code, name, country, type):
        self.code = code
        self.name = name
        self.country = country
        self.type = type


class CommonModel:
    def __init__(self, target_date, hour, model_config_path=MODEL_PATH, results_path=RESULTS_PATH):
        """
        Проведение расчета
        :param model_config_path: папка с json-файлами модели
        :param fixed_bids_path: папка с json-файлами заявок
        :param hour: целевой час
        """
        self.target_date = target_date
        self.hour = hour
        self.results_path = results_path

        self.countries = self.load_countries(os.path.join(model_config_path, 'countries.json'))
        self.nodes = self.load_nodes(os.path.join(model_config_path, 'nodes.json'))
        self.sections = self.load_sections(os.path.join(model_config_path, 'sections.json'))
        self.load_section_limits(os.path.join(model_config_path, 'section_limits.xlsx'))
        self.mgp_price = self.load_mgp_prices(os.path.join(model_config_path, 'mgp_prices.xlsx'))  # страна из - страна в -> цена
        # self.currencies = self.load_currencies(os.path.join(model_config_path, 'currencies.json'))
        self.participants = self.load_participants(os.path.join(model_config_path, 'participants.json'))
        self.currencies = self.stub_currencies()

    def load_countries(self, file_name):
        with open(file_name, 'r', encoding='utf8') as fp:
            input_data = json.load(fp)
        return {country['code']: Country(country['code'], country['name']) for country in input_data}

    def load_nodes(self, file_name):
        with open(file_name, 'r', encoding='utf8') as fp:
            input_data = json.load(fp)
        return {
            node['node_code']: Node(node['node_code'], node['node_name'], self.countries[node['country_code']])
            for node in input_data
        }

    def load_sections(self, file_name):
        with open(file_name, 'r', encoding='utf8') as fp:
            input_data = json.load(fp)

        def cut_countries(data):
            return {self.countries[c['country_code']] for c in data}

        def distr_rule(rule_data):
            return {
                self.countries[r['country_code']]: {
                    self.nodes[node_mgp['node_code']]: node_mgp['mpg_list']
                    for node_mgp in r['node_mgp']
                }
                for r in rule_data
            }

        sections = [
            Section(
                self.nodes[sec['node_from']], self.nodes[sec['node_to']],
                cut_countries(sec['cut_countries']),
                distr_rule(sec['distr_rule'])
            )
            for sec in input_data
        ]
        return {section.code: section for section in sections}

    def load_section_limits(self, file_name):
        target_date, hour, sections = self.target_date, self.hour, self.sections
        wb = xlrd.open_workbook(file_name)
        data = wb.sheet_by_index(0)._cell_values
        for row in data[1:]:
            d = xlrd.xldate.xldate_as_datetime(row[COL_DATE], 0)
            if d.date() == target_date and row[COL_HOUR] == hour:
                s = self.sections[row[COL_SECTION]]  # type: Section
                s.pmax_fw = float(row[COL_PMAX])
                s.pmax_bw = float(row[COL_PMIN])

        assert all(
            s.pmax_bw is not None and s.pmax_fw is not None
            for s in sections.values()
        ), "Нет данных по ограничениям на переток у {}".format(','.join(
            s_code
            for s_code, s in sections.items()
            if s.pmax_bw is not None and s.pmax_fw is not None
        ))

    def load_mgp_prices(self, file_name):
        target_date, hour = self.target_date, self.hour
        wb = xlrd.open_workbook(file_name)
        data = wb.sheet_by_index(0)._cell_values

        mgp_prices = dict()
        for row in data[1:]:
            d = xlrd.xldate.xldate_as_datetime(row[COL_DATE], 0)
            if d.date() == target_date and row[COL_HOUR] == hour:
                assert row[COL_COUNTRY_FROM] in self.countries and row[COL_COUNTRY_TO] in self.countries
                mgp_prices['{}-{}'.format(row[COL_COUNTRY_FROM], row[COL_COUNTRY_TO])] = float(row[COL_MGP_PRICE])

        return mgp_prices

    def load_participants(self, file_name):
        with open(file_name, 'r', encoding='utf8') as fp:
            input_data = json.load(fp)

        return {
            p['_id']: Participant(p['_id'], p['name'], self.countries[p['country_code']], p['dir'])
            for p in input_data
        }


    def stub_currencies(self):
        currencies = dict()
        for c in self.countries.values():
            currencies[c] = 1
        return currencies
    #
    #
    # def load_currencies(self, file_name):
    #     with open(file_name, 'r', encoding='utf8') as fp:
    #         input_data = json.load(fp)
    #
    #     currencies = dict()
    #     for row in input_data:
    #         assert row['country_code'] in self.countries
    #         currencies[self.countries[row['country_code']]] = float(row['conversion_rate'])
    #
    #     return currencies


    @staticmethod
    def check_opt_status(results):
        if (results.solver.status == SolverStatus.ok) and \
                (results.solver.termination_condition == TerminationCondition.optimal):
            # print('Оптимальное решение найдено')
            pass
        elif results.solver.termination_condition == TerminationCondition.infeasible:
            raise RuntimeError('Несовместная задача')
        else:
            # Что-то еще не так
            raise RuntimeError(results.solver)
