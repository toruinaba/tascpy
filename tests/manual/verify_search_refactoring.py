
import sys
import os
import math
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step

def create_test_collection():
    c = ColumnCollection(step=[], columns={})
    c.step = Step(values=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    
    # Values: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    vals = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    c.add_column("Data", NumberColumn(None, "Data", None, values=vals))
    
    # Values with None: [1, None, 3, None, 5, 6, 7, 8, 9, 10]
    vals_none = [1.0, None, 3.0, None, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    c.add_column("WithNone", NumberColumn(None, "WithNone", None, values=vals_none))

    return c

def test_search_by_value():
    c = create_test_collection()
    # Data > 50 -> 60, 70, 80, 90, 100 -> Indices 5,6,7,8,9
    indices = c.ops.search_by_value("Data", ">", 50.0)
    print(f"DEBUG: indices={indices}")
    assert len(indices) == 5
    assert indices == [5, 6, 7, 8, 9]
    print("Pass: search_by_value")

def test_search_by_range():
    c = create_test_collection()
    # Data 30-60 -> 30, 40, 50, 60 -> Indices 2,3,4,5
    indices = c.ops.search_by_range("Data", 30.0, 60.0)
    assert indices == [2, 3, 4, 5]
    print("Pass: search_by_range")

def test_search_top_n():
    c = create_test_collection()
    # Top 3 -> 100, 90, 80 -> Indices 9, 8, 7 -> Sorted: 7, 8, 9
    indices = c.ops.search_top_n("Data", n=3)
    assert indices == [7, 8, 9]
    print("Pass: search_top_n")

def test_search_by_step_range():
    c = create_test_collection()
    # Step 2.0-5.0 -> Indices 2, 3, 4, 5
    indices, meta = c.ops.search_by_step_range(min=2.0, max=5.0)
    assert indices == [2, 3, 4, 5]
    print("Pass: search_by_step_range")

def test_search_missing_values():
    c = create_test_collection()
    # WithNone has None at 1, 3
    indices = c.ops.search_missing_values(columns=["WithNone"])
    assert indices == [1, 3]
    
    # Data has no missing
    indices_data = c.ops.search_missing_values(columns=["Data"])
    assert indices_data == []
    print("Pass: search_missing_values")

def test_search_by_condition():
    c = create_test_collection()
    # Data > 50 AND Data < 80 -> 60, 70 -> Indices 5, 6
    # Row data is passed as dict
    def condition(row):
        return row["Data"] > 50.0 and row["Data"] < 80.0

    indices = c.ops.search_by_condition(condition_func=condition)
    # Also valid with columns arg (optimization)
    indices_opt = c.ops.search_by_condition(condition_func=condition, columns=["Data"])
    
    assert indices == [5, 6]
    assert indices_opt == [5, 6]
    print("Pass: search_by_condition")

if __name__ == "__main__":
    test_search_by_value()
    test_search_by_range()
    test_search_top_n()
    test_search_by_step_range()
    test_search_missing_values()
    test_search_by_condition()
