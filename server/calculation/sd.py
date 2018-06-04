from pyomo.environ import *
from itertools import chain, product
import os
import json
from datetime import datetime, timedelta
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
        model = ConcreteModel()
        self.model = model
        if len(self.sd):
            model.sd = Set(initialize=self.sd)
            model.sections = Set(initialize=self.sections.values())
            def fb(model, sd):
                return (0, sd.volume)
            model.x = Var(model.sd, initialize=0, within=NonNegativeReals, bounds=fb)

            def target_function(model):
                return sum(model.x[sd] for sd in model.sd)

            def section_flow_limits(model, section):
                return (
                    - section.pmax_bw,
                    sum(model.x[sd] * section.flow_dir(*sd.country_from_to())
                        for sd in model.sd),
                    section.pmax_fw
                )

            model.cost = Objective(rule=target_function, sense=maximize)
            model.section_flow_limits = Constraint(model.sections, rule=section_flow_limits)

            opt = SolverFactory(SOLVER, executable=SOLVER_PATH)
            results = opt.solve(model)
            self.check_opt_status(results)
            # model.solutions.load_from(results)

            # Фиксируем сумму объемов оптимального решения
            total_vol = sum(var.value for var in model.x.values())

            @simple_constraintlist_rule
            def total_vol_fix(model):
                return target_function(model) == total_vol

            model.fix_vol_limit = Constraint(rule=total_vol_fix)

            max_sec = set()
            new_max_sec = self.get_max_sections()
            while new_max_sec > max_sec:
                # выравнивание сниженных объемов СД по сработавшим сечениям
                def equalize_target_function(model):
                    # res = 0
                    limit_sds = set()
                    for dir, section in new_max_sec:
                        for sd in model.sd:
                            if dir == section.flow_dir(*sd.country_from_to()):
                                # res += model.x[sd] * model.x[sd]
                                limit_sds.add(sd)
                    return sum(model.x[sd] * model.x[sd] for sd in limit_sds)
                    # return res

                model.del_component('cost')
                model.cost = Objective(rule=equalize_target_function, sense=minimize)
                # results = opt.solve(model, tee=True)
                results = opt.solve(model)
                # self.check_opt_status(results)  doesn't work correctly with cplex
                max_sec = new_max_sec
                new_max_sec =  self.get_max_sections()



            for sd, var in model.x.items():
                sd.accepted_volume = round(var.value, 3)

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
    def sd_runner_core(cls, input_data, dates, model_config_path=MODEL_PATH, sd_path=INPUT_PATH, results_path=RESULTS_PATH):
        section_limits = list()
        for d in dates:
            day = {'target_date': d, 'limit_type': 'SECTION_FLOW_LIMIT_EX', 'hours': []}
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
                        'pmax_fw': round(sec.pmax_fw - sec.calc_flow(m.model, m.sd), 3),
                        'pmax_bw': round(sec.pmax_bw + sec.calc_flow(m.model, m.sd), 3)
                    } for sec in m.sections.values()
                )

        return input_data, section_limits

    @classmethod
    def sd_runner(cls, model_config_path=MODEL_PATH, sd_path=INPUT_PATH, results_path=RESULTS_PATH):
        input_data = cls.load_sd(sd_path)
        dates = set(chain.from_iterable([[gr['tdate'] for gr in sd['values']] for sd in input_data]))
        sd, section_limits = cls.sd_runner_core(input_data, dates, model_config_path, sd_path, results_path)

        for c in sd:
            c['dateStart'] = '{:%Y-%m-%d}'.format(c['dateStart'])
            c['dateEnd'] = '{:%Y-%m-%d}'.format(c['dateEnd'])
            for v in c['values']:
                v['tdate'] = '{:%Y-%m-%d}'.format(v['tdate'])

        for c in section_limits:
            c['target_date'] = '{:%Y-%m-%d}'.format(c['target_date'])

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

        old_section_limits = list(db.section_limits.find({'limit_type': 'SECTION_FLOW_LIMIT_FC', 'session_id': {'$exists': False}}))
        session = db.sessions.find_one({'_id': session_id})
        dates = [session['startDate'] + timedelta(i) for i in range(1 + (session['finishDate'] - session['startDate']).days)]

        sd, section_limits = cls.sd_runner_core(cls.load_sd(session_id), dates)

        for c in sd:
            db.sdd.find_one_and_replace({'_id': c['_id']}, c)

        for s in section_limits:
            s['session_id'] = session_id
        db.section_limits.remove({'session_id': session_id})
        db.section_limits.insert_many(section_limits)
        
        for row in section_limits:
            del row['_id']
            row['limit_type'] += '_mod'
            for hour in row['hours']:
                for section in hour['sections']:
                    [old_sec] = [s for o in old_section_limits for h in o['hours'] for s in h['sections']
                                if o['target_date'] == row['target_date'] and h['hour'] == hour['hour'] and s['section_code'] == section['section_code']]
                    section['pmax_fw'] += old_sec['extra_limit_ex_fw']
                    section['pmax_bw'] += old_sec['extra_limit_ex_bw']

        db.section_limits.insert_many(section_limits)
