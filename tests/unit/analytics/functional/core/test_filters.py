import pytest
import numpy as np
from tascpy.analytics.functional.filters import (
    eq, neq, compare, in_range, is_valid, filter_valid_rows, duplicated_indices,
    remove_outliers_mask
)

def test_eq():
    arr = np.array([1, 2, 3, 2, 1])
    np.testing.assert_array_equal(eq(arr, 2), [False, True, False, True, False])
    np.testing.assert_array_equal(eq(arr, 2.1, tolerance=0.15), [False, True, False, True, False])

def test_neq():
    arr = np.array([1, 2, 3])
    np.testing.assert_array_equal(neq(arr, 2), [True, False, True])

def test_compare():
    arr = np.array([1, 2, 3, np.nan])
    np.testing.assert_array_equal(compare(arr, ">", 1), [False, True, True, False])
    np.testing.assert_array_equal(compare(arr, "<=", 2), [True, True, False, False])
    with pytest.raises(ValueError):
        compare(arr, "invalid", 2)

def test_in_range():
    arr = np.array([1, 2, 3, 4, 5])
    np.testing.assert_array_equal(in_range(arr, 2, 4), [False, True, True, True, False])
    np.testing.assert_array_equal(in_range(arr, 2, 4, inclusive=False), [False, False, True, False, False])

def test_is_valid():
    arr = np.array([1, np.nan, 3])
    np.testing.assert_array_equal(is_valid(arr), [True, False, True])
    arr_obj = np.array([1, None, "test"], dtype=object)
    np.testing.assert_array_equal(is_valid(arr_obj), [True, False, True])

def test_filter_valid_rows():
    data = {
        "A": np.array([1, 2, np.nan, 4]),
        "B": np.array([1, np.nan, np.nan, 4])
    }
    np.testing.assert_array_equal(filter_valid_rows(data, mode="any"), [True, False, False, True])
    np.testing.assert_array_equal(filter_valid_rows(data, mode="all"), [True, True, False, True])

def test_duplicated_indices():
    data = {"A": np.array([1, 1, 2, 2, 3, 3, 3]), "B": np.array([10, 10, 20, 20, 30, 40, 40])}
    res = duplicated_indices(data, mode="consecutive", dup_type="all")
    assert res == [0, 2, 4, 5]


