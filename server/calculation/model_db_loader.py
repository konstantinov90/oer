import pymongo

from .model_file_loader import ModelFileLoader

db = pymongo.MongoClient().inter_market

class ModelDbLoader(ModelFileLoader):
    @classmethod
    def load_mgp_prices(cls, target_date, hour):
        return db.mgp_prices.find_one({
            'date_from': target_date,
            'date_to': target_date,
            'period_type': 'D',
            'graph_type': 'FR',
        })['sections']

    @classmethod
    def load_section_limits(cls, target_date, hour):
        [hour] = [row for row in db.section_limits.find_one({
            'target_date': target_date,
        })['hours'] if row['hour'] == hour]
        return hour['sections']

    @classmethod
    def load_participants(cls):
        return list(db.rio.find())

    @classmethod
    def load_sections(cls):
        return list(db.sections.find())

    @classmethod
    def load_nodes(cls):
        return list(db.nodes.find())

    @classmethod
    def load_countries(cls):
        return list(db.countries.find())
