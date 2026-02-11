
import pytest
import numpy as np
from tascpy.utils.data import (
    filter_none_values,
    moving_average,
    detect_outliers_ratio,
    diff_step,
    diff_xy,
    integrate_xy,
)

class TestFilterNoneValues:
    def test_basic(self):
        data = [1, None, 3, None, 5]
        assert filter_none_values(data) == [1, 3, 5]

    def test_all_none(self):
        data = [None, None, None]
        assert filter_none_values(data) == []

    def test_empty(self):
        assert filter_none_values([]) == []

    def test_no_none(self):
        data = [1, 2, 3]
        assert filter_none_values(data) == [1, 2, 3]


class TestMovingAverage:
    def test_basic_numpy(self):
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        # window=3.
        # [1, 2, 3] -> 2
        # [2, 3, 4] -> 3
        # [3, 4, 5] -> 4
        # Edges handled by 'same' convolution in implementation
        # index 0: window covers effectively index 0, 1 -> avg(1, 2) = 1.5? 
        # Wait, implementation uses padding with 0 but denominator adjusts for valid values.
        # Center of window size 3 at index 0 covers indices -1, 0, 1.
        # -1 is invalid/outside. 0 is 1.0. 1 is 2.0.
        # Sum = 3.0. Count = 2. Avg = 1.5.
        
        result = moving_average(data, window_size=3)
        assert len(result) == 5
        assert result[2] == 3.0
        assert result[0] == 1.5 
        assert result[-1] == 4.5 # avg(4, 5)

    def test_with_none(self):
        data = [1.0, None, 3.0, 5.0]
        # None becomes NaN
        # index 1 (None): window [1.0, NaN, 3.0]. Valid: 1.0, 3.0. Sum=4.0. Count=2. Avg=2.0.
        result = moving_average(data, window_size=3)
        assert result[1] == 2.0
        assert result[0] == 1.0 # window [NaN(idx-1), 1.0, NaN(None)] -> valid only 1.0. Avg 1.0.

    def test_empty(self):
        assert moving_average([]) == []


class TestDetectOutliersRatio:
    def test_basic_detection(self):
        # 10, 10, 10, 100(outlier), 10, 10
        data = [10.0] * 3 + [100.0] + [10.0] * 3
        # Use higher threshold to avoid neighbors being detected due to MA pull
        outliers = detect_outliers_ratio(data, window_size=3, threshold=1.0)
        # 100 vs neighbors 10, 10. avg ~ 40 or so. 
        # diff = |100 - 40| = 60. denominator=40. ratio=1.5 > 0.5.
        assert len(outliers) > 0
        indices = [o[0] for o in outliers]
        assert 3 in indices
        assert outliers[0][1] == 100.0

    def test_no_outliers(self):
        data = [10.0, 11.0, 10.5, 10.2, 10.8]
        outliers = detect_outliers_ratio(data, threshold=0.5)
        assert len(outliers) == 0

    def test_data_shorter_than_window(self):
        with pytest.raises(ValueError):
            detect_outliers_ratio([1.0, 2.0], window_size=3)


class TestDiffStep:
    def test_basic_diff(self):
        data = [1.0, 3.0, 6.0, 10.0]
        # result[0] = data[0] = 1.0
        # result[1] = 3-1 = 2
        # result[2] = 6-3 = 3
        # result[3] = 10-6 = 4
        result = diff_step(data)
        assert result == [1.0, 2.0, 3.0, 4.0]

    def test_empty_error(self):
        with pytest.raises(ValueError, match="empty"):
            diff_step([])


class TestDiffXY:
    def test_central(self):
        x = [0, 1, 2, 3, 4]
        y = [0, 1, 4, 9, 16] # y = x^2, dy/dx = 2x
        # x=0: forward: (1-0)/(1-0) = 1. True=0.
        # x=1: central: (4-0)/(2-0) = 2. True=2.
        # x=2: central: (9-1)/(3-1) = 4. True=4.
        # x=3: central: (16-4)/(4-2) = 6. True=6.
        # x=4: backward: (16-9)/(4-3) = 7. True=8.
        
        result = diff_xy(x, y, method="central")
        assert result[1] == 2.0
        assert result[2] == 4.0
        assert result[3] == 6.0

    def test_forward(self):
        x = [0, 1, 2]
        y = [0, 1, 4]
        # x=0: (1-0)/1 = 1
        # x=1: (4-1)/1 = 3
        # x=2: repeat last -> 3
        result = diff_xy(x, y, method="forward")
        assert result == [1.0, 3.0, 3.0]

    def test_backward(self):
        x = [0, 1, 2]
        y = [0, 1, 4]
        # x=0: repeat first -> 1.0 (from index 1 calculation)
        # x=1: (1-0)/1 = 1.0
        # x=2: (4-1)/1 = 3.0
        # Wait, implementation:
        # dx = [1, 1]
        # dy = [1, 3]
        # d = [1, 3]
        # insert at 0: d[0]=1. -> [1, 1, 3]
        result = diff_xy(x, y, method="backward")
        assert result == [1.0, 1.0, 3.0]

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            diff_xy([1, 2], [1])


class TestIntegrateXY:
    def test_linear_integration(self):
        # y = x. Integral = 0.5 * x^2 + C. from 0
        x = [0.0, 1.0, 2.0, 3.0]
        y = [0.0, 1.0, 2.0, 3.0]
        
        # 0: init(0) + x[0]*y[0] = 0 + 0*0 = 0
        # 1: 0 + 0.5*(0+1)*1 = 0.5. True 0.5*1^2 = 0.5
        # 2: 0.5 + 0.5*(1+2)*1 = 0.5 + 1.5 = 2.0. True 0.5*2^2 = 2.0
        # 3: 2.0 + 0.5*(2+3)*1 = 2.0 + 2.5 = 4.5. True 0.5*3^2 = 4.5
        
        result = integrate_xy(x, y)
        np.testing.assert_allclose(result, [0.0, 0.5, 2.0, 4.5])

    def test_with_nans(self):
        x = [0, 1, 2]
        y = [1, np.nan, 2]
        # expect all None/NaN except maybe first if strict
        # Implementation returns [NaN, NaN, ...] converted to [None, None, ...] 
        # EXCEPT first point calculation: result[0] = init + x[0]*y[0].
        # if x[0], y[0] valid, result[0] is valid float. Remainder are NaN.
        
        result = integrate_xy(x, y)
        assert result[0] is not None
        assert result[1] is None
