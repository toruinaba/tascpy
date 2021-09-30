from pathlib import Path
import src.tascpy as tp

class Test_results:
    def test_result(self):
        path = Path('./data/W-N.txt')
        with tp.Reader(path) as f:
            res = tp.Results(f)
        assert res.dict
