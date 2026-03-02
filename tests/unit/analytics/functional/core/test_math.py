import pytest
import numpy as np
import math
from tascpy.analytics.functional.math import (
    add, subtract, multiply, divide, diff, integrate, evaluate_expression,
    sin, cos, tan, exp, log, sqrt, power, abs_values, round_values, normalize
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
    np.testing.assert_allclose(res, [2.0, 4.0, 6.0])

def test_evaluate_functional():
    data = {
        "A": np.array([1.0, 2.0]),
        "B": np.array([3.0, 4.0])
    }
    res = evaluate_expression(data, "A + B * 2")
    assert res == [7.0, 10.0]

def test_trig_functions():
    np.testing.assert_allclose(sin(np.array([0, np.pi/2])), [0, 1], atol=1e-10)
    np.testing.assert_allclose(cos(np.array([0, np.pi])), [1, -1], atol=1e-10)

def test_log_functions():
    res = log(np.array([1.0, math.e]))
    np.testing.assert_allclose(res, [0.0, 1.0])

def test_normalize():
    arr = np.array([1.0, 2.0, 3.0])
    minmax = normalize(arr, method="minmax")
    np.testing.assert_array_equal(minmax, [0.0, 0.5, 1.0])
