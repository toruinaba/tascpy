import pytest
import numpy as np
from tascpy.analytics.functional.combine import (
    switch_by_step,
    blend_by_step,
    sum_columns,
    average_columns,
    conditional_select,
    custom_combine
)

def test_switch_by_step_value():
    steps = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    v1 = np.array([10] * 10)
    v2 = np.array([20] * 10)
    
    # threshold 5, compare_mode "value"
    res = switch_by_step(steps, v1, v2, threshold=5, compare_mode="value", by_step_value=True)
    
    np.testing.assert_array_equal(res[:5], 10)
    np.testing.assert_array_equal(res[5:], 20)

def test_switch_by_step_index():
    steps = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
    v1 = np.array([10] * 10)
    v2 = np.array([20] * 10)
    
    # threshold idx 5
    res = switch_by_step(steps, v1, v2, threshold=5, compare_mode="index", by_step_value=False)
    
    np.testing.assert_array_equal(res[:5], 10)
    np.testing.assert_array_equal(res[5:], 20)

def test_blend_by_step_linear():
    steps = np.arange(10.0)
    v1 = np.full(10, 10.0)
    v2 = np.full(10, 20.0)
    
    res = blend_by_step(
        steps, v1, v2, 
        start=2, end=7, 
        compare_mode="index", by_step_value=False, blend_method="linear"
    )
    
    assert res[1] == 10.0
    assert res[2] == 10.0
    assert res[7] == 20.0
    assert res[8] == 20.0
    assert res[4] == 14.0  # t=2/5=0.4 => 10*(0.6) + 20*0.4 = 6+8=14

def test_sum_columns():
    arr1 = np.array([1, 2, 3])
    arr2 = np.array([4, 5, 6])
    res = sum_columns([arr1, arr2])
    np.testing.assert_array_equal(res, [5, 7, 9])

def test_average_columns():
    arr1 = np.array([10, 20, 30])
    arr2 = np.array([30, 40, 50])
    res = average_columns([arr1, arr2])
    np.testing.assert_array_equal(res, [20, 30, 40])

def test_conditional_select():
    v1 = np.array([10, 10, 10])
    v2 = np.array([20, 20, 20])
    cond = np.array([0.1, 0.6, 0.9])
    
    res = conditional_select(v1, v2, cond, threshold=0.5, compare=">")
    np.testing.assert_array_equal(res, [20, 10, 10])

def test_custom_combine():
    v1 = np.array([1, 2, 3])
    v2 = np.array([4, 5, 6])
    def my_add(x, y):
        return x + y + 1
    
    res = custom_combine(v1, v2, combine_func=my_add)
    np.testing.assert_array_equal(res, [6, 8, 10])
