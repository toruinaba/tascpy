
import sys
import os
import numpy as np
import pytest

# Apply path trick
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn, StringColumn
from tascpy.core.step import Step
from tascpy.analytics.operations.core.filters import (
    filter_by_value,
    filter_out_none,
    remove_consecutive_duplicates_across,
    remove_outliers,
    filter_by_condition,
    remove_steps
)

def create_test_collection():
    steps = [0.1 * i for i in range(10)]
    # A: 0, 1, 2, ...
    col_a_vals = [float(i) for i in range(10)] 
    # B: 0, 0, 1, 1, 2, 2, ... (consecutive dups potential)
    col_b_vals = [float(i // 2) for i in range(10)]
    # C: Outlier at index 5 (100.0)
    col_c_vals = [10.0] * 10
    col_c_vals[5] = 100.0
    
    coll = ColumnCollection(step=Step(values=steps), columns={})
    coll.add_column("A", NumberColumn("CH1", "A", "N", col_a_vals))
    coll.add_column("B", NumberColumn("CH2", "B", "mm", col_b_vals))
    coll.add_column("C", NumberColumn("CH3", "C", "N", col_c_vals))
    return coll

def test_filter_by_value():
    c = create_test_collection()
    # A > 5 -> 6,7,8,9 (length 4)
    # Wait, filter_by_value checks equality.
    # A == 5.0 -> 1 row
    res = filter_by_value(c, "A", 5.0)
    assert len(res) == 1
    assert res.step.values[0] == 0.5
    print("Pass: filter_by_value")

def test_remove_steps():
    c = create_test_collection()
    # Remove steps 0.2 and 0.5
    res = remove_steps(c, steps=[0.2, 0.5])
    assert len(res) == 8 # 10 - 2
    assert 0.2 not in res.step.values
    assert 0.5 not in res.step.values
    print("Pass: remove_steps")

def test_remove_outliers():
    c = create_test_collection()
    # C has outlier at index 5 (step 0.5)
    # With window=3, the outlier (100) affects neighbor MAs.
    # MA ~ 40. Val=10. Diff=30. Ratio=0.75 > 0.5.
    # So indices 4, 5, 6 might be removed.
    res = remove_outliers(c, "C", window_size=3, threshold=0.5)
    # print(f"Debug: remove_outliers len(res)={len(res)}")
    assert len(res) == 7 
    # Check index 5 is gone (step 0.5)
    # Check index 5 is gone (step 0.5)
    # Original steps: 0, 0.1, 0.2 ...
    # Result steps should lack 0.5
    assert 0.5 not in res.step.values
    print("Pass: remove_outliers")

def test_raw_input_support():
    # Test high-level abstraction (raw inputs)
    
    # filter_by_value on raw list
    data = [1, 2, 3, 2, 1]
    # mask = [False, True, False, True, False]
    mask = filter_by_value(data, 2)
    assert mask == [False, True, False, True, False]
    print("Pass: raw_input_filter_by_value")
    
    # remove_steps on raw steps
    steps = [0.1, 0.2, 0.3, 0.4]
    # remove 0.2
    # mask = [True, False, True, True]
    mask_steps = remove_steps(steps, [0.2])
    assert mask_steps == [True, False, True, True]
    print("Pass: raw_input_remove_steps")

def test_raw_input_remove_outliers():
    data_out = [10.0, 10.0, 10.0, 100.0, 10.0]
    # mask = [True, True, True, False, True]
    mask_out = remove_outliers(data_out, window_size=3, threshold=0.5)
    assert mask_out[3] == False
    assert mask_out[0] == True
    print("Pass: raw_input_remove_outliers")

def test_raw_input_multicolumn():
    # Test filter_out_none with raw dict
    from tascpy.analytics.operations.core.filters import filter_out_none, remove_consecutive_duplicates_across
    
    data = {
        "A": [1, 2, None, 4],
        "B": [1, 2, 3, 4]
    }
    # Mode='any' -> Row 2 (index 2) has None in A. Exclude.
    # Mask: [True, True, False, True]
    mask = filter_out_none(data, mode="any")
    assert mask == [True, True, False, True]
    print("Pass: raw_input_filter_out_none")
    
    # Test remove_consecutive_duplicates_across with raw dict
    data_dup = {
        "A": [1, 1, 2, 2],
        "B": [10, 10, 20, 20]
    }
    # Index 0: Keep
    # Index 1: A=1(prev 1), B=10(prev 10) -> Dup. Skip.
    # Index 2: A=2(prev 1), B=20(prev 10) -> Changed. Keep.
    # Index 3: A=2(prev 2), B=20(prev 20) -> Dup. Skip.
    # Indices: [0, 2]
    indices = remove_consecutive_duplicates_across(data_dup, columns=["A", "B"])
    assert indices == [0, 2]
    print("Pass: raw_input_remove_consecutive_duplicates_across")

if __name__ == "__main__":
    test_filter_by_value()
    test_remove_steps()
    test_remove_outliers()
    test_raw_input_support()
    test_raw_input_remove_outliers()
    test_raw_input_multicolumn()
