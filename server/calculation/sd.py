from model import CommonModel, DIR, SOLVER, SOLVER_PATH, MODEL_PATH
from pyomo.environ import *
from itertools import chain, product
import os
import json
from datetime import datetime


INPUT_PATH = 'sd'
RESULTS_PATH = 'results_sd'


class Sd:
    def __init__(self, id, target_date, hour, buyer, seller, section, volume, price):
        self.id = id
        self.target_date = target_date
        self.hour = hour
        self.buyer = buyer
        self.seller = seller
        self.section = section
        self.volume = volume
        self.accepted_volume = 0
        self.price = price

    def country_from_to(self):
        """Функция нужна для расчета перетоков по сечению"""
        return self.seller.country, self.buyer.country

    def __lt__(self, other):
        return (self.buyer.code, self.seller.code, self.section.code) < \
                (other.buyer.code, other.seller.code, other.section.code)

    def __str__(self):
        return 'СД {}->{} volume={:<5}({:<5})'.format(self.seller.code, self.buyer.code, self.accepted_volume, self.volume)


class SdModel(CommonModel):
    def __init__(self, target_date, hour, model_config_path=MODEL_PATH,
                 sd_path=INPUT_PATH, results_path=RESULTS_PATH, input_data=None):
        super().__init__(target_date, hour, model_config_path, results_path)
        if input_data is None:
            input_data = load_sd(sd_path)
        self.sd = self.parse_sd(input_data)

    def parse_sd(self, sd_data):
        target_date, hour = self.target_date, self.hour
        res = []

        for sd in sd_data:
            gr_val = [gr for gr in sd['values']
                      if datetime.strptime(gr['tdate'], '%Y-%m-%d').date() == self.target_date and gr['hour'] == self.hour]
            assert len(gr_val) <= 1
            if len(gr_val):
                gr_val = gr_val[0]
            else:
                continue
            res.append(
                Sd(
                    sd['_id'],
                    target_date,
                    hour,
                    self.participants[sd['buyer']],
                    self.participants[sd['seller']],
                    self.sections[sd['section']],
                    gr_val['volume'],
                    gr_val['price']
                )
            )
        return res

    def get_max_sections(self):
        res = set()
        for section in self.sections.values():
            # flow = sum(self.model.x[sd].value * section.flow_dir(*sd.country_from_to()) for sd in self.sd)
            flow = section.calc_flow(self.model, self.sd)
            if flow > section.pmax_fw - 1e-6:
                res.add((1, section))
            elif flow < - section.pmax_bw + 1e-6:
                res.add((-1, section))
        return res


    def reduce_graph(self):
        for sd in self.sd:
            sd.accepted_volume = 0

    def save_results_to_file(self):
        results = list()
        for sd in self.sd:
            sd_res = dict()
            sd_res['_id'] = sd.id
            sd_res['target_date'] = '{:%Y-%m-%d}'.format(sd.target_date)
            sd_res['hour'] = sd.hour
            sd_res['buyer'] = sd.buyer.code
            sd_res['seller'] = sd.seller.code
            sd_res['accepted_volume'] = sd.accepted_volume
            results.append(sd_res)

        with open(os.path.join(self.results_path, 'sd_results.json'), 'w', encoding='utf8') as fp:
            json.dump(results, fp)


def load_sd(sd_path):
    with open(os.path.join(sd_path, 'sd.json'), 'r', encoding='utf8') as fp:
        return json.load(fp)

def sd_runner(model_config_path=MODEL_PATH, sd_path=INPUT_PATH, results_path=RESULTS_PATH):
    input_data = load_sd(sd_path)
    section_limits = list()
    dates = set(chain.from_iterable([[datetime.strptime(gr['tdate'], '%Y-%m-%d').date() for gr in sd['values']] for sd in input_data]))
    for d in dates:
        str_date = '{:%Y-%m-%d}'.format(d)
        for h in range(24):
            m = SdModel(d, h, model_config_path, sd_path, results_path, input_data)
            m.reduce_graph()
            for sd in m.sd:
                sd_data = next(s for s in input_data if s['_id'] == sd.id)
                graph_data = next(v for v in sd_data['values'] if v['tdate'] == str_date and v['hour'] == h)
                graph_data['accepted_volume'] = sd.accepted_volume
            section_limits.extend(
                {
                    'tdate': str_date,
                    'hour': h,
                    'Section_code': sec.code,
                    'LimitType': 'SECTION_FLOW_LIMIT_EX',
                    'pmax_fw': 0,
                    'pmax_bw': 0,
                } for sec in m.sections.values()
            )

    with open(os.path.join(results_path, 'sd_results.json'), 'w', encoding='utf8') as fp:
        json.dump(input_data, fp)
    with open(os.path.join(results_path, 'section_limits_ex.json'), 'w', encoding='utf8') as fp:
        json.dump(section_limits, fp)
