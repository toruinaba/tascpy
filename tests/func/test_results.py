from pathlib import Path
import src.tascpy as tp

class Test_results:
    def test_result(self):
        path = Path('./data/W-N.txt')
        with tp.Reader(path) as f:
            res = tp.Experimental_data(f)
        data = res["P_total"]
        print(data.to_dict())
        step = res.get_step(10)
        # print(step.to_dict())
        # assert res.dict

