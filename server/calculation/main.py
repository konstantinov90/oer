from spot import SpotModel, SpotModelAug
from sd import SdModel, SdModelAug
from datetime import date, datetime
from time import time


if __name__ == '__main__':
        t = time()
        # m = SpotModel(target_date=date(2018, 6, 18), hour=0)
        # m.calc()
        # m.print_result()
        # m = SdModel(target_date=date(2018, 6, 18), hour=0)
        # m.reduce_graph()
        # m.save_results_to_file()
        # SdModel.sd_runner()
        SdModelAug.sd_runner(11)
        # SpotModelAug.spot_runner(datetime(2018, 6, 18))
        # SpotModel.spot_runner()
        print(time() - t)