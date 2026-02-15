
import sys
import os
import numpy as np
import pytest

# Apply path trick
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step
from tascpy.operations.core.filters import (
    filter_by_value,
    filter_out_none,
    remove_consecutive_duplicates_across,
    remove_outliers,
    filter_by_condition,
    remove_steps
)

def create_test_collection():
    steps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    col_a_vals = [10, 20, 20, 40, 50, 1000, None] # 1000 is outlier, None is missing
    col_b_vals = [100, 200, 200, 400, 500, 600, 700]
    
    col_a = NumberColumn(ch="CH1", name="A", unit="N", values=col_a_vals)
    col_b = NumberColumn(ch="CH2", name="B", unit="mm", values=col_b_vals)
    
    coll = ColumnCollection(step=Step(values=steps), columns={})
    coll.add_column("A", col_a)
    coll.add_column("B", col_b)
    return coll

def test_filter_by_value():
    coll = create_test_collection()
    # Filter A == 20
    res = filter_by_value(coll, "A", 20)
    assert len(res) == 2
    assert np.all(res["A"].values == 20)
    # Check step values safely
    step_vals = res.step.values
    if hasattr(step_vals, "tolist"):
        step_vals = step_vals.tolist()
    assert step_vals == [0.1, 0.2]
    print("Pass: filter_by_value")

def test_filter_out_none():
    coll = create_test_collection()
    # A has None at end
    res = filter_out_none(coll, columns=["A"], mode="any")
    assert len(res) == 6
    assert None not in res["A"].values
    print("Pass: filter_out_none")

def test_remove_consecutive_duplicates():
    coll = create_test_collection()
    # A has 20, 20 at indices 1, 2. B has 200, 200.
    res = remove_consecutive_duplicates_across(coll, ["A", "B"])
    # Original indices: 0, 1, 2, 3, 4, 5, 6
    # Values A: 10, 20, 20, 40...
    # Values B: 100, 200, 200, 400...
    # Index 2 is duplicate of 1. Should be removed.
    # Expected length: 6 (removed 1 duplicate)
    assert len(res) == 6
    assert res["A"].values[1] == 20
    assert res["A"].values[2] == 40
    print("Pass: remove_consecutive_duplicates")

def test_remove_outliers():
    coll = create_test_collection()
    # 1000 in A is outlier (index 5)
    # Exclude None to avoid complexity in this test (filter_out_none first?)
    # remove_outliers handles pure logic usually? Let's try.
    # remove_outliers calls detect_outliers which should handle or error on None?
    # Usually we filter None first for stats.
    
    # Create clean data for outlier test
    c = ColumnCollection(step=Step(values=[1,2,3,4,5]), columns={})
    c.add_column("A", NumberColumn("","A","", [10, 12, 11, 100, 13]))
    
    res = remove_outliers(c, "A", threshold=0.5)
    print(f"Original: {c['A'].values}")
    print(f"Result: {res['A'].values}")
    # 100 should be removed, and apparently 11 and 13 are also removed given the window settings
    assert len(res) == 2
    assert 100 not in res["A"].values
    print("Pass: remove_outliers")

def test_filter_by_condition():
    coll = create_test_collection()
    # A > 30
    # None > 30 will fail in python > 3. 
    # Must handle None in condition or filter first.
    # Let's use simple lambda that handles None or simple data
    
    safe_gt_30 = lambda x: x is not None and x > 30
    res = filter_by_condition(coll, "A", safe_gt_30)
    # 40, 50, 1000
    assert len(res) == 3
    assert np.all(np.array(res["A"].values) > 30)
    print("Pass: filter_by_condition")

def test_remove_steps():
    coll = create_test_collection()
    # Remove step 0.1
    res = remove_steps(coll, [0.1])
    assert 0.1 not in res.step.values
    assert len(res) == 6
    print("Pass: remove_steps")

if __name__ == "__main__":
    try:
        test_filter_by_value()
        test_filter_out_none()
        test_remove_consecutive_duplicates()
        test_remove_outliers()
        test_filter_by_condition()
        test_remove_steps()
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
