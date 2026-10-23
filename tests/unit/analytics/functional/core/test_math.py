import pytest
import numpy as np
import math
from tascpy.analytics.functional.core.math import (
    add, subtract, multiply, divide, diff, integrate,
    log, sqrt, power, abs_values, round_values, normalize,
)

def test_add_functional():
    res = add(np.array([1.0, 2.0]), np.array([3.0, 4.0]))
    np.testing.assert_array_equal(res, [4.0, 6.0])

def test_subtract_functional():
    res = subtract(np.array([3.0, 4.0]), 1.0)
    np.testing.assert_array_equal(res, [2.0, 3.0])

def test_multiply_functional():
    res = multiply(np.array([2.0, 3.0]), np.array([4.0, 5.0]))
    np.testing.assert_array_equal(res, [8.0, 15.0])

def test_divide_functional():
    res = divide(np.array([10.0, 20.0]), np.array([2.0, 5.0]))
    np.testing.assert_array_equal(res, [5.0, 4.0])

def test_diff_functional():
    y = np.array([1.0, 4.0, 9.0])
    x = np.array([1.0, 2.0, 3.0])
    res = diff(y, x, method="central")
    np.testing.assert_allclose(res, [3.0, 4.0, 5.0])

def test_integrate_functional():
    y = np.array([2.0, 2.0, 2.0])
    x = np.array([1.0, 2.0, 3.0])
    res = integrate(y, x, method="trapezoid")
    np.testing.assert_allclose(res, [0.0, 2.0, 4.0])

def test_log_functions():
    res = log(np.array([1.0, math.e]))
    np.testing.assert_allclose(res, [0.0, 1.0])

def test_normalize():
    arr = np.array([1.0, 2.0, 3.0])
    minmax = normalize(arr, method="minmax")
    np.testing.assert_array_equal(minmax, [0.0, 0.5, 1.0])

def test_integrate_starts_at_initial_value():
    np.testing.assert_allclose(integrate(y=[1.0, 1.0, 1.0], x=[10.0, 11.0, 12.0]), [0.0, 1.0, 2.0])
    np.testing.assert_allclose(integrate(y=[1.0, 1.0], x=[10.0, 11.0], initial_value=5.0), [5.0, 6.0])


def test_integrate_follows_path_order():
    # 往復する x でも並べ替えず経路に沿って積分する（戻り区間は面積が差し引かれる）
    np.testing.assert_allclose(integrate(y=[0.0, 2.0, 2.0], x=[0.0, 1.0, 0.0]), [0.0, 1.0, -1.0])
