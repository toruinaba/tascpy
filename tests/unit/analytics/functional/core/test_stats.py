import pytest
import numpy as np
import math
from tascpy.analytics.functional.stats import (
    moving_average,
    detect_outliers,
    gaussian_filter
)

def test_moving_average():
    data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    res = moving_average(data, window_size=3)
    expected = [15.0, 20.0, 30.0, 40.0, 50.0, 60.0, 65.0]
    np.testing.assert_allclose(res, expected, atol=1e-6)

    # Test with None
    data_with_none = [10.0, None, 30.0, None, 50.0, 60.0, 70.0]
    res_none = moving_average(data_with_none, window_size=3)
    assert res_none[1] == 20.0
    assert res_none[3] == 40.0

def test_detect_outliers():
    data = [10.0, 20.0, 100.0, 40.0, 50.0, 200.0, 70.0]
    res = detect_outliers(data, window_size=3, threshold=0.5)
    expected = [0, 0, 1, 0, 0, 1, 0]
    np.testing.assert_array_equal(res, expected)

def test_gaussian_filter():
    data = [10.0] * 20
    res = gaussian_filter(data, sigma=1.0)
    np.testing.assert_allclose(res, data, atol=1e-6)


