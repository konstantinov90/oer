from pyomo.environ import *
from itertools import chain, product
import os
import os.path
import json
import functools
from datetime import datetime

try:
    from model import CommonModel, DIR, SOLVER, SOLVER_PATH, MODEL_PATH
except ModuleNotFoundError:
    from .model import CommonModel, DIR, SOLVER, SOLVER_PATH, MODEL_PATH
    from .model_db_loader import ModelDbLoader
    import pymongo


BIDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bids')
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results_spot')

def is_price_form(bid):
    total_filled_volume = sum(nb.filled_volume for nb in bid.node_bids.values())
    return (total_filled_volume > 1e-6 and total_filled_volume < bid.volume - 1e-6)


class Bid:
    def __init__(self, id, interval_num, country, dir, volume):
        self.id = id
        self.interval_num = interval_num
        self.country = country
        self.dir = dir
        self.volume = volume  # объемы считаются в дельтах из-за того, что неясно как сортировать в разных странах
        self.node_bids = dict()

    def translate_prices(self):
        pass

    def __lt__(self, other):
        return (self.country.code, self.dir, self.volume) < \
                (other.country.code, other.dir, other.volume)

    def __str__(self):
        return 'BID {} {:>4} volume={:<5}'.format(self.country.code, self.dir, self.volume)


class NodeBid:
    def __init__(self, bid, section, node, price, mgp_price=0):
        self.bid = bid
        self.section = section
        self.node = node
        self.price = max(price - mgp_price, 0)
        self.mgp_price = mgp_price
        self.filled_volume = None
        self.basic_liability = 0.0
        self.mgp_liability = 0.0

    def translate_prices(self):
        pass

    def country_from_to(self):
        # Эта функция нужна для расчета перетоков по сечению
        # Перетоки считаем по заявкам на покупку. На продажу возвращаем одну и ту же страну, иначе переток задвоится
        if self.bid.dir == 'buy':
            return (self.node.country, self.bid.country)
        else:
            return (self.bid.country, self.bid.country)

    def __lt__(self, other):
        return (self.node.code, self.bid.dir, self.bid.country.code, self.price, self.bid.volume) < \
                (other.node.code, other.bid.dir, other.bid.country.code, other.price, other.bid.volume)

    def __str__(self):
        return '{} {:<4} от {}: price={:<5.0f} volume={:<5.0f} filled_volume={:<5.0f}'.format(
            self.node.code, self.bid.dir, self.bid.country.code,
            self.price, self.bid.volume, self.filled_volume)


class SpotModel(CommonModel):
    def __init__(self, target_date, hour, model_config_path=MODEL_PATH,
                 bids_path=BIDS_PATH, results_path=RESULTS_PATH, bids_data=None):
        super().__init__(target_date, hour, model_config_path, results_path)
        # self.fixed_bids_path = bids_path

        # Закоментирована загрузка заявок, которая считывала все файлы в директории
        # Послений вариант смотрит толдько один файл bids.json - массив заявок
        # self.fixed_bids = list(chain.from_iterable(
        #     self.load_bid(os.path.join(bids_path, file))
        #     for file in os.listdir(bids_path)
        #     if file.endswith('.json')
        # ))

        if bids_data is None:
            bids_data = load_bid(bids_path)
        self.fixed_bids = self.parse_bid(bids_data)

        self.bids = []
        self.node_bids = None
        self.opt_model = None

    def parse_bid(self, bid_data):
        """ загрузка часовой заявки """
        target_date, hour = self.target_date, self.hour
        if isinstance(bid_data, list):  # раньше заявки приходили в отдельных файлах, сейчас в одном массиве (файле)
            return list(chain.from_iterable(self.parse_bid(b) for b in bid_data))
        participant = self.participants[bid_data['trader_code']]
        country = participant.country
        bid_dir = bid_data['dir']
        if target_date != bid_data['target_date']:
            return []
        try:
            hour_data = next(obj for obj in bid_data['hours'] if obj['hour'] == hour)
        except StopIteration:
            raise ValueError('Час {} отсутствует в заявке {} {}'.format(hour, country.code, bid_dir))

        assert 0 < len(hour_data['intervals']) <= 3, \
            'Пар <цена-количество> должно быть от 1 до 3, заявка: {} {}'.format(country.code, bid_dir)
        bids = []
        for interval in hour_data['intervals']:
            interval_num = interval['interval_num']
            bid = Bid(bid_data['_id'], interval_num, country, bid_dir, interval['volume'])
            prices = interval['prices']
            if bid.dir == 'sell':
                for data in prices:
                    section = self.sections[data['section_code']]
                    node_from = section.node_from
                    node_to = section.node_to
                    if node_from.country == bid.country:
                        node = node_from
                    elif node_to.country == bid.country:
                        node = node_to
                    else:
                        raise ValueError('Заявка на может быть только в сечение на границе своей страны')
                    p = float(data['price']) * self.currencies[bid.country]
                    bid.node_bids[node] = NodeBid(bid, section, node, p)
                assert len(bid.node_bids) == sum(n.country == bid.country for n in self.nodes.values()), \
                    'Заявка подана не во все сечения: {}'.format(bid)
            elif bid.dir == 'buy':
                for data in prices:
                    section = self.sections[data['section_code']]
                    if bid.country not in section.distr_rule:
                        raise ValueError('Заявка на может быть только в сечение на границе своей страны')

                    p = float(data['price']) * self.currencies[bid.country]
                    for node, mgp_list in section.distr_rule[bid.country].items():
                        mgp_price = sum(self.mgp_price[mgp_countries] for mgp_countries in mgp_list)
                        bid.node_bids[node] = NodeBid(bid, section, node, p, mgp_price)

                # теперь может быть меньше 4, т.к. стоимость МГП может быть больше заявки
                # assert len(bid.node_bids) == 4, 'Заявка подана не во все сечения: {}'.format(bid)
            else:
                raise ValueError('Неверное направление в заявке')

            bids.append(bid)

        return bids

    def add_bid(self, bid):
        self.bids.extend(self.parse_bid(bid))

    def make_model(self):
        bids = self.fixed_bids + self.bids
        for b in bids:
            for nb in b.node_bids.values():
                if nb.price <= 0:
                    nb.filled_volume = 0
        self.node_bids = [nb for b in bids for nb in b.node_bids.values()]

        model = ConcreteModel()
        model.nodes = Set(initialize=self.nodes.values())
        model.bids = Set(initialize=bids)
        model.node_bids = Set(initialize=self.node_bids)
        model.sections = Set(initialize=self.sections.values())
        model.x = Var(model.node_bids, initialize=0, within=NonNegativeReals)

        def wellfare_function(model):
            return sum(node_bid.price * model.x[node_bid] * DIR[node_bid.bid.dir]
                       for node_bid in model.node_bids)

        @simple_constraintlist_rule
        def node_balance_constraint(model, node):
            # Сумма принятых объемов заявок покупки в каждом узле равна сумме продажи
            return sum(DIR[node_bid.bid.dir] * model.x[node_bid]
                       for node_bid in model.node_bids if node_bid.node == node) == 0

        def section_flow_limits(model, section):
            return (
                - section.pmax_bw,
                sum(model.x[node_bid] * section.flow_dir(*node_bid.country_from_to())
                    for node_bid in model.node_bids),
                section.pmax_fw
            )

        @simple_constraintlist_rule
        def bid_node_sum(model, bid):
            return sum(model.x[node_bid] for node_bid in bid.node_bids.values() if node_bid in model.x) <= bid.volume

        model.cost = Objective(rule=wellfare_function, sense=maximize)
        model.node_balance_bids = Constraint(model.nodes, rule=node_balance_constraint)
        model.section_flow_limits = Constraint(model.sections, rule=section_flow_limits)
        model.bid_node_sum = Constraint(model.bids, rule=bid_node_sum)
        self.cut_node_bids(model)

        self.opt_model = model
        return model

    @staticmethod
    def cut_node_bids(model):
        sos_pairs = []
        for node in model.nodes:
            node_bids = [nb for nb in model.node_bids if nb.node == node]
            sos_pairs.extend(
                [(b1, b2) for b1, b2 in product(node_bids, node_bids)
                  if b1.bid.dir == 'buy' and b2.bid.dir == 'sell' and b1.price < b2.price]
            )
        model.sos_pairs = Set(initialize=sos_pairs)
        sos_set = dict()
        for s in sos_pairs:
            sos_set[s] = s
        model.node_forbidden_bids = SOSConstraint(model.sos_pairs, var=model.x, index=sos_set, sos=1)
        # model.pprint()

    def calc_liability(self):
        node_bids = self.node_bids
        #
        # шаг первый. все покупают / продают по узловой цене
        for nb in node_bids:  # type: NodeBid
            nb.basic_liability = DIR[nb.bid.dir] * nb.filled_volume * nb.node.price
            nb.mgp_liability = nb.filled_volume * nb.mgp_price

        assert abs(sum(nb.basic_liability for nb in node_bids)) < 1, 'Небаланс в обязательствах'
        # TODO: что это? разобраться и вернуть
        # assert all(
        #     DIR[nb.bid.dir] * nb.price * nb.filled_volume - nb.basic_liability > -1e-3
        #     for nb in node_bids
        # ), 'Нарушения условия заявки'

    def calc(self):
        """Выполняет цикл расчета"""

        model = self.make_model()
        opt = SolverFactory(SOLVER, executable=SOLVER_PATH)
        model.dual = Suffix(direction=Suffix.IMPORT)
        results = opt.solve(model)
        self.check_opt_status(results)
        model.solutions.load_from(results)

        for node_bid, var in model.x.items():
            node_bid.filled_volume = var.value

        for sec in model.section_flow_limits:
            sec.flow = sec.calc_flow(model, self.node_bids)
        #     sec.price = model.dual[model.section_flow_limits[sec]]

        # for node in model.node_balance_bids:
        #     node.price = model.dual[model.node_balance_bids[node]]
        for node in model.nodes:
            current_bids = [nb for nb in model.node_bids if nb.node == node]
            gen_bids = [nb for nb in current_bids if nb.bid.dir == 'sell' and nb.filled_volume > 1e-6]
            gen_bids.sort(key=lambda x: x.price)
            con_bids = [nb for nb in current_bids if nb.bid.dir == 'buy' and nb.filled_volume > 1e-6]
            con_bids.sort(key=lambda x: -x.price)
            if len(gen_bids) > 0:
                #     TODO: смотреть по маржинальности с учетом группы заявок
                if is_price_form(gen_bids[-1].bid):
                    node.price = gen_bids[-1].price
                elif is_price_form(con_bids[-1].bid):
                    node.price = con_bids[-1].price
                else:
                    # выбирается просто минимальная цена, это цена генератора
                    node.price = min(gen_bids[-1].price, con_bids[-1].price)
            else:
                assert len(con_bids) == 0
                node.price = 0
        # self.calc_liability()


    def print_result(self):
        print('Сечения:')
        for sec in self.sections.values():
            if sec.price is not None:
                print('\t{:<30}: flow={:<5.0f} price={:<5.0f}'.format(str(sec), sec.flow, sec.price))
            else:
                print('\t{:<30}: flow={:<5.0f}'.format(str(sec), sec.flow))

        print('Узлы:')
        for node in sorted(self.nodes.values()):
            if node.price is not None:
                print('\t{:<40}: price={:<5.0f}'.format(str(node), node.price))

        print('Узловые заявки: ')
        for node_bid in sorted(list(self.node_bids)):
            if node_bid.filled_volume != 0.0:
                print('\t{} result_price={:>8.3f}'.format(
                    node_bid, abs((node_bid.basic_liability + node_bid.mgp_liability) / node_bid.filled_volume)))
            else:
                print('\t{} result_price={:>8.3f}'.format(node_bid, 0.0))

    def clear_results(self):
        for sec in self.sections.values():
            sec.flow = None
            sec.price = None
        for node in self.nodes.values():
            node.price = None

        for bid in self.fixed_bids:
            for nb in bid.node_bids.values():
                nb.filled_volume = None

        self.bids = []


    @classmethod
    def spot_runner_core(cls, model_config_path, bids_data):
        dates = list(set([b['target_date'] for b in bids_data]))
        assert len(dates) == 1, 'Файл с заявками должен быть на одни сутки'
        d = dates[0]
        results = list()
        for h in range(24):
            hour_res = dict()
            hour_res['hour'] = h
            hour_res['tdate'] = d
            m = cls(d, h, model_config_path, '', '', bids_data=bids_data)
            m.calc()
            m.print_result()

            for node_bid, var in m.opt_model.x.items():
                bid_section = next(s for s in m.sections.values() if s.node_from == node_bid.node or s.node_to == node_bid.node)
                input_data = next(b for b in bids_data if b['_id'] == node_bid.bid.id)
                hour_data = next(bh for bh in input_data['hours'] if bh['hour'] == h)
                interval_data = next(bi for bi in hour_data['intervals'] if bi['interval_num'] == node_bid.bid.interval_num)
                try:
                    node_data = next(bn for bn in interval_data['prices'] if bn['section_code'] == bid_section.code)
                except StopIteration:
                    interval_data['prices'].append({
                        'price': node_bid.price,
                        'section_code': bid_section.code,
                        'filled_volume': var.value,
                    })
                else:
                    node_data['filled_volume'] = var.value

            hour_res['nodes'] = [{'code': n.code, 'price': n.price} for n in m.opt_model.nodes]
            hour_res['sections'] = [{'code': s.code, 'flow': s.calc_flow(m.opt_model, m.node_bids)} for s in m.opt_model.sections]
            results.append(hour_res)

        return bids_data, results

    @classmethod
    def load_section_limits_for_subclass(cls, target_date, hour):
        return cls.LOADER.load_section_limits(target_date, hour, 'SECTION_FLOW_LIMIT_DAM')

    @classmethod
    def load_bid(cls, bids_path):
        with open(os.path.join(bids_path, 'bids.json'), 'r', encoding='utf8') as fp:
            bids = json.load(fp)
        for bid in bids:
            bid['target_date'] = datetime.strptime(bid['target_date'], '%Y-%m-%d')
        return bids

    @classmethod
    def spot_runner(cls, model_config_path=MODEL_PATH, bids_path=BIDS_PATH, results_path=RESULTS_PATH):
        bids_data = cls.load_bid(bids_path)

        bids_data, results = cls.spot_runner_core(model_config_path, bids_data)

        for bid in bids_data:
            bid['target_date'] = '{:%Y-%m-%d}'.format(bid["target_date"])

        for res in results:
            res['tdate'] = '{:%Y-%m-%d}'.format(res["tdate"])

        with open(os.path.join(results_path, 'bids_results.json'), 'w', encoding='utf8') as fp:
            json.dump(bids_data, fp)

        with open(os.path.join(results_path, 'results.json'), 'w', encoding='utf8') as fp:
            json.dump(results, fp)



class SpotModelAug(SpotModel):
    @classmethod
    def load_sec_lims(cls, target_date, hour, futures_session_id):
        return cls.LOADER.load_section_limits(target_date, hour, 'SECTION_FLOW_LIMIT_DAM', futures_session_id)

    @classmethod
    def load_bid(cls, session_id):
        db = pymongo.MongoClient().inter_market
        return list(db.bids.find({'session_id': session_id}))

    @classmethod
    def spot_runner(cls, session_id, futures_session_id, model_config_path=MODEL_PATH):
        CommonModel.set_loader(ModelDbLoader)
        cls.load_section_limits_for_subclass = functools.partial(cls.load_sec_lims, futures_session_id=futures_session_id)

        bids_data = cls.load_bid(session_id)

        bids_data, results = cls.spot_runner_core(model_config_path, bids_data)

        db = pymongo.MongoClient().inter_market
    
        for bid in bids_data:
            db.bids.find_one_and_replace({'_id': bid['_id']}, bid)

        db.spot_results.delete_one({'session_id': session_id})
        db.spot_results.insert({'session_id': session_id, 'hours': results})
