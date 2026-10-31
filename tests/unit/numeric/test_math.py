import pytest
import numpy as np
import math
from tascpy.numeric.math import diff, integrate, log, normalize

def test_diff():
    y = np.array([1.0, 4.0, 9.0])
    x = np.array([1.0, 2.0, 3.0])
    res = diff(x, y, method="central")
    np.testing.assert_allclose(res, [3.0, 4.0, 5.0])

def test_integrate():
    y = np.array([2.0, 2.0, 2.0])
    x = np.array([1.0, 2.0, 3.0])
    res = integrate(x, y, method="trapezoid")
    np.testing.assert_allclose(res, [0.0, 2.0, 4.0])

def test_log_functions():
    res = log(np.array([1.0, math.e]))
    np.testing.assert_allclose(res, [0.0, 1.0])

def test_normalize():
    arr = np.array([1.0, 2.0, 3.0])
    minmax = normalize(arr, method="minmax")
    np.testing.assert_array_equal(minmax, [0.0, 0.5, 1.0])

def test_integrate_starts_at_initial_value():
    np.testing.assert_allclose(integrate([10.0, 11.0, 12.0], [1.0, 1.0, 1.0]), [0.0, 1.0, 2.0])
    np.testing.assert_allclose(integrate([10.0, 11.0], [1.0, 1.0], initial_value=5.0), [5.0, 6.0])


def test_integrate_follows_path_order():
    # 往復する x でも並べ替えず経路に沿って積分する（戻り区間は面積が差し引かれる）
    np.testing.assert_allclose(integrate([0.0, 1.0, 0.0], [0.0, 2.0, 2.0]), [0.0, 1.0, -1.0])


@pytest.mark.parametrize("method, expected", [
    ("backward", [np.nan, 10.0, np.nan, 8.0, 5.0]),
    ("forward", [10.0, np.nan, 8.0, 5.0, np.nan]),
])
def test_diff_one_sided_marks_undefined_points_nan(method, expected):
    x, y = np.array([0.0, 1.0, 1.0, 2.0, 4.0]), np.array([0.0, 10.0, 12.0, 20.0, 30.0])
    np.testing.assert_allclose(diff(x, y, method=method), expected)


def test_diff_central_zero_step_is_nan_without_warning():
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        res = diff(np.array([0.0, 1.0, 1.0, 2.0]), np.array([0.0, 10.0, 12.0, 20.0]), method="central")
    assert np.isfinite(res).sum() < len(res)
    assert not np.isinf(res).any()
