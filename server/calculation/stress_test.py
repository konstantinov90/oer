from model import Model
import random
import pickle
from tqdm import trange


countries = ['BLR', 'RUS', 'ARM', 'KAZ', 'KGZ']

sections = {
    'BLR': ['RUS-BLR', ],
    'ARM': ['RUS-ARM', ],
    'RUS': ['RUS-BLR', 'RUS-ARM', 'RUS-KAZ'],
    'KAZ': ['RUS-KAZ', 'KAZ-KGZ'],
    'KGZ': ['KAZ-KGZ', ]
}


class RandomAgent:
    def __init__(self, country, dir, vol_bounds, price_bounds):
        self.country = country
        self.dir = dir
        self.vol_bounds = vol_bounds
        self.price_bounds = price_bounds
        self.allowed_sections = sections[country]

    def create_bid(self):
        if self.dir == 'buy':
            return {
                "country_code": self.country,
                "dir": self.dir,
                "intervals": [
                    {
                        "volume": random.randint(*self.vol_bounds),
                        "price": random.randint(*self.price_bounds)
                    }
                    for _ in range(random.randint(1, 3))
                ]
            }
        else:
            return {
                "country_code": self.country,
                "dir": self.dir,
                "intervals": [
                    {
                        "volume": random.randint(*self.vol_bounds),
                        "prices": [
                            {"section_code": section, "price": random.randint(*self.price_bounds)}
                            for section in self.allowed_sections
                        ]
                    }
                    for _ in range(random.randint(1, 3))
                ]
            }


if __name__ == "__main__":
    price_bounds = (1, 5000)
    vol_bounds = (5, 25)
    agents = []

    # агенты на продажу
    for c in countries:
        for _ in range(10):
            agents.append(RandomAgent(c, 'sell', vol_bounds, price_bounds))

    # агенты на покупку
    for c in countries:
        for _ in range(10):
            agents.append(RandomAgent(c, 'buy', vol_bounds, price_bounds))

    m = Model('model', 'bids')

    for _ in trange(100):
        bids_archive = []
        for a in agents:
            b = a.create_bid()
            bids_archive.append(b)
            m.add_bid(b)
        try:
            m.calc()
        except:
            with open('./bids/bids.pickle', 'wb') as f:
                pickle.dump(bids_archive, f)
            raise
        m.clear_results()
