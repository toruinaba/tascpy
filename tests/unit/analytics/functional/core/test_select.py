import pytest
import numpy as np
from tascpy.analytics.functional.select import (
    select_indices,
    fetch_near_step,
    split_by_integers,
    split_at_indices,
)

def test_select_indices_by_value():
    steps = np.array([10.0, 20.0, 30.0, 40.0])
    
    indices, meta = select_indices(steps, steps=[20.0, 40.0], by_step_value=True)
    assert indices == [1, 3]
    assert meta["selected_steps"] == [20.0, 40.0]
    assert meta["missing_steps"] == []

def test_select_indices_with_tolerance():
    steps = np.array([10.0, 20.0, 30.0])
    indices, meta = select_indices(steps, steps=[19.5, 31.0], by_step_value=True, tolerance=1.0)
    assert indices == [1, 2]

def test_select_indices_missing():
    steps = np.array([10.0, 20.0])
    indices, meta = select_indices(steps, steps=[30.0], by_step_value=True)
    assert indices == []
    assert meta["missing_steps"] == [30.0]

def test_select_indices_by_index():
    steps = np.array([10.0, 20.0, 30.0])
    indices, meta = select_indices(steps, steps=[0, 2], by_step_value=False)
    assert indices == [0, 2]
    assert meta["selected_steps"] == [10.0, 30.0]

def test_fetch_near_step():
    values = np.array([1.0, 2.0, 5.0, 10.0])
    assert fetch_near_step(values, 4.0) == [2]
    assert fetch_near_step(values, 1.2) == [0]

def test_split_by_integers():
    markers = np.array([1, 2, 1, 3, 2])
    res = split_by_integers(5, markers)
    assert len(res) == 3
    np.testing.assert_array_equal(res[0], [0, 2])
    np.testing.assert_array_equal(res[1], [1, 4])
    np.testing.assert_array_equal(res[2], [3])

def test_split_at_indices():
    res = split_at_indices(10, [3, 7])
    assert res == [slice(0, 3, None), slice(3, 7, None), slice(7, 10, None)]
