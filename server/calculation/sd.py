from pyomo.environ import *
from itertools import chain, product
import os
import json
from datetime import datetime
try:
    from model import CommonModel, DIR, SOLVER, SOLVER_PATH, MODEL_PATH
except ModuleNotFoundError:
    import pymongo
    from .model import CommonModel, DIR, SOLVER, SOLVER_PATH, MODEL_PATH
    from .model_db_loader import ModelDbLoader


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
                      if gr['tdate'] == self.target_date and gr['hour'] == self.hour]
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

    @classmethod
    def load_section_limits_for_subclass(cls, target_date, hour):
        return cls.LOADER.load_section_limits(target_date, hour, 'SECTION_FLOW_LIMIT_FC')

    @classmethod
    def load_sd(cls, sd_path):
        with open(os.path.join(sd_path, 'sd.json'), 'r', encoding='utf8') as fp:
            sd = json.load(fp)
        for c in sd:
            c['dateStart'] = datetime.strptime(c['dateStart'], '%Y-%m-%d')
            c['dateEnd'] = datetime.strptime(c['dateEnd'], '%Y-%m-%d')
            for v in c['values']:
                v['tdate'] = datetime.strptime(v['tdate'], '%Y-%m-%d')
        return sd

    @classmethod
    def sd_runner_core(cls, input_data, model_config_path=MODEL_PATH, sd_path=INPUT_PATH, results_path=RESULTS_PATH):
        section_limits = list()
        dates = set(chain.from_iterable([[gr['tdate'] for gr in sd['values']] for sd in input_data]))
        for d in dates:
            day = {'target_date': d, 'limit_type': 'SECTION_FLOW_LIMIT_DAM', 'hours': []}
            section_limits.append(day)
            for h in range(24):
                hour = {'hour': h, 'sections': []}
                day['hours'].append(hour)

                m = cls(d, h, model_config_path, sd_path, results_path, input_data)
                m.reduce_graph()
                for sd in m.sd:
                    sd_data = next(s for s in input_data if s['_id'] == sd.id)
                    graph_data = next(v for v in sd_data['values'] if v['tdate'] == d and v['hour'] == h)
                    graph_data['accepted_volume'] = sd.accepted_volume

                hour['sections'].extend(
                    {
                        'section_code': sec.code,
                        'pmax_fw': m.sections[sec.code].pmax_fw,
                        'pmax_bw': m.sections[sec.code].pmax_bw,
                    } for sec in m.sections.values()
                )

        return input_data, section_limits

    @classmethod
    def sd_runner(cls, model_config_path=MODEL_PATH, sd_path=INPUT_PATH, results_path=RESULTS_PATH):
        sd, section_limits = cls.sd_runner_core(cls.load_sd(sd_path), model_config_path, sd_path, results_path)

        for c in sd:
            c['dateStart'] = '{:%Y-%m-%d}'.format(c['dateStart'])
            c['dateEnd'] = '{:%Y-%m-%d}'.format(c['dateEnd'])
            for v in c['values']:
                v['tdate'] = '{:%Y-%m-%d}'.format(v['tdate'])

        for c in section_limits:
            c['tdate'] = '{:%Y-%m-%d}'.format(c['tdate'])

        with open(os.path.join(results_path, 'sd_results.json'), 'w', encoding='utf8') as fp:
            json.dump(sd, fp)
        with open(os.path.join(results_path, 'section_limits_ex.json'), 'w', encoding='utf8') as fp:
            json.dump(section_limits, fp)

class SdModelAug(SdModel):
    @classmethod
    def load_sec_lims(cls, target_date, hour):
        return cls.LOADER.load_section_limits(target_date, hour, 'SECTION_FLOW_LIMIT_FC')

    @classmethod
    def load_sd(cls, session_id):
        db = pymongo.MongoClient().inter_market
        return list(db.sdd.find({'sessionId': session_id, 'status': 'registered'}))

    @classmethod
    def sd_runner(cls, session_id):
        CommonModel.set_loader(ModelDbLoader)
        cls.load_section_limits_for_subclass = cls.load_sec_lims

        db = pymongo.MongoClient().inter_market
        sd, section_limits = cls.sd_runner_core(cls.load_sd(session_id))

        for c in sd:
            db.sdd.find_one_and_replace({'_id': c['_id']}, c)

        for s in section_limits:
            s['session_id'] = session_id
        db.section_limits.remove({'session_id': session_id})
        db.section_limits.insert_many(section_limits)
