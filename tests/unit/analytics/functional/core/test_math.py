import pytest
import numpy as np
import math
from tascpy.analytics.functional.core.math import (
    add, subtract, multiply, divide, diff, integrate, evaluate_expression,
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

def test_evaluate_functional():
    data = {
        "A": np.array([1.0, 2.0]),
        "B": np.array([3.0, 4.0])
    }
    res = evaluate_expression(data, "A + B * 2")
    np.testing.assert_allclose(res, [7.0, 10.0])


def test_evaluate_missing_is_nan():
    data = {"A": np.array([1.0, np.nan])}
    np.testing.assert_array_equal(evaluate_expression(data, "A * 2"), [2.0, np.nan])

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


@pytest.mark.parametrize("expression, expected", [
    ("A if A > 3 else 0", [0.0, 0.0, 0.0, 4.0, 5.0]),
    ("1 < A < 4", [0.0, 1.0, 1.0, 0.0, 0.0]),
    ("(A > 1) and not (A > 4)", [0.0, 1.0, 1.0, 1.0, 0.0]),
    ("A > 4 or A < 2", [1.0, 0.0, 0.0, 0.0, 1.0]),
    ("max(A, 3) + pi * 0", [3.0, 3.0, 3.0, 4.0, 5.0]),
    ("2", [2.0] * 5),
])
def test_evaluate_vectorized_syntax(expression, expected):
    data = {"A": np.array([1.0, 2.0, 3.0, 4.0, 5.0])}
    np.testing.assert_allclose(evaluate_expression(data, expression), expected)


def test_evaluate_invalid_results_and_missing_rows_are_nan():
    data = {"A": np.array([0.0, -1.0, np.nan, 4.0])}
    np.testing.assert_array_equal(evaluate_expression(data, "1 / A"), [np.nan, -1.0, np.nan, 0.25])
    np.testing.assert_array_equal(evaluate_expression(data, "log(A)"), [np.nan, np.nan, np.nan, np.log(4.0)])
    np.testing.assert_array_equal(evaluate_expression(data, "A if A > 3 else 0"), [0.0, 0.0, np.nan, 4.0])


@pytest.mark.parametrize("expression", [
    "A.__class__", '__import__("os")', "(lambda: 1)()", "A[0]", "[A]", "log(x=A)", "open('f')",
])
def test_evaluate_rejects_unsafe_syntax(expression):
    with pytest.raises(ValueError):
        evaluate_expression({"A": np.array([1.0])}, expression)


def test_evaluate_errors():
    with pytest.raises(KeyError):
        evaluate_expression({"A": np.array([1.0])}, "B + 1")
    with pytest.raises(ValueError, match="構文"):
        evaluate_expression({"A": np.array([1.0])}, "A +")
    with pytest.raises(ValueError, match="数値に変換できません"):
        evaluate_expression({"s": np.array(["x"])}, "s * 2")
