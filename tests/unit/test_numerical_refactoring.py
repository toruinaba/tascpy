import pytest
import numpy as np
import math
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.numeric import stats as f_stats

class TestNumericalRefactoring:
    @pytest.fixture
    def collection(self):
        return ColumnCollection(
            step=[1, 2, 3, 4, 5],
            columns={
                "A": [1.0, 2.0, 3.0, 4.0, 5.0],
                "B": [10.0, 20.0, 30.0, 40.0, 50.0],
                "C": [1.0, -1.0, 0.0, None, 5.0],
                "D": [None, None, None, None, None],
            }
        )

    def test_utils_data_moving_average(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        # Window 3. 
        # Asymmetric (default):
        # i=0: [1, 2] -> 1.5
        # i=1: [1, 2, 3] -> 2.0
        # i=2: [2, 3, 4] -> 3.0
        # i=3: [3, 4, 5] -> 4.0
        # i=4: [4, 5] -> 4.5
        ma = f_stats.moving_average(data, window_size=3)
        expected = [1.5, 2.0, 3.0, 4.0, 4.5]
        np.testing.assert_allclose(ma, expected)

        # Test with None
        data_none = [1.0, None, 3.0]
        # i=0: [1, Nan] -> 1.0 (mean of [1])
        # i=1: [1, Nan, 3] -> 2.0 (mean of [1, 3])
        # i=2: [Nan, 3] -> 3.0 (mean of [3])
        ma_none = f_stats.moving_average(data_none, window_size=3)
        # implementation details:
        # np.convolve used. 
        # i=0 (center): window covers -1..1. Index 0, 1. Values 1, Nan. Valid: 1. Mean: 1.
        # i=1 (center): window covers 0..2. Index 0, 1, 2. Values 1, Nan, 3. Valid: 1, 3. Mean: 2.
        # i=2 (center): window covers 1..3. Index 1, 2. Values Nan, 3. Valid: 3. Mean: 3.
        expected_none = [1.0, 2.0, 3.0] 
        np.testing.assert_allclose(ma_none, expected_none)

    def test_math_add_numpy(self, collection):
        # A + B
        res = collection.ops.add("A", "B", result_column="A+B").end()
        np.testing.assert_array_equal(res["A+B"].values, [11.0, 22.0, 33.0, 44.0, 55.0])
        
        # A + C (with None)
        res2 = collection.ops.add("A", "C", result_column="A+C").end()
        # 1+1=2, 2-1=1, 3+0=3, 4+None=None, 5+5=10
        # 4+None=None -> NaN
        expected = np.array([2.0, 1.0, 3.0, np.nan, 10.0])
        np.testing.assert_allclose(res2["A+C"].values, expected, equal_nan=True)

    def test_transform_log(self, collection):
        # log(A)
        res = collection.ops.log("A", result_column="log(A)").end()
        expected = [math.log(x) for x in range(1, 6)]
        np.testing.assert_allclose(res["log(A)"].values, expected)
        
        # log(C) -> 1.0 (0.0), -1.0 (None), 0.0 (None), None (None), 5.0 (log(5))
        res2 = collection.ops.log("C", result_column="log(C)").end()
        vals = res2["log(C)"].values
        assert vals[0] == 0.0
        assert np.isnan(vals[1]) # -1.0
        assert np.isnan(vals[2]) # 0.0
        assert np.isnan(vals[3]) # None
        assert abs(vals[4] - math.log(5.0)) < 1e-10

    def test_math_calculate(self, collection):
        res = collection.ops.calculate(lambda A, B: A + B * 2, result_column="result").end()
        np.testing.assert_array_equal(res["result"].values, [21.0, 42.0, 63.0, 84.0, 105.0])

    def test_math_calculate_conditional(self, collection):
        res = collection.ops.calculate(lambda A: np.where(A > 3, A, 0), result_column="r").end()
        np.testing.assert_array_equal(res["r"].values, [0, 0, 0, 4.0, 5.0])

    def test_math_calculate_none_handling(self, collection):
        vals = collection.ops.calculate(lambda C: C * 2, result_column="result_none").end()["result_none"].values
        np.testing.assert_array_equal(vals, [2.0, -2.0, 0.0, np.nan, 10.0])

    def test_stats_detect_outliers(self, collection):
        # Create data with obvious outlier
        col = Column("X", ch="1", unit="N", values=[10, 10, 10, 100, 10, 10])
        c = ColumnCollection({"X": col}, step=[1,2,3,4,5,6])
        
        # stats.detect_outliers
        # It creates a flag column (0/1)
        res = c.ops.detect_outliers("X", window_size=3, threshold=0.5, result_column="outlier(X)").end()
        # 100 should be outlier
        # The result column name is "outlier({column})" by default in stats.py
        flags = res["outlier(X)"].values
        assert flags[3] == 1
        assert flags[0] == 0
