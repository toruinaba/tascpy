
import sys
import os
import numpy as np
import pytest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn, StringColumn
from tascpy.core.step import Step
import tascpy.analytics.operations.core.interpolate # Register operations

def create_test_collection():
    c = ColumnCollection(step=[], columns={})
    # Step: 0, 10, 20, 30, 40
    c.step = Step(values=[0.0, 10.0, 20.0, 30.0, 40.0])
    
    # Val: 0, 100, 200, 300, 400 (Linear)
    vals = [0.0, 100.0, 200.0, 300.0, 400.0]
    c.add_column("Val", NumberColumn(None, "Val", "unit", values=vals))
    
    # Meta (String): "A", "B", "C", "D", "E"
    strs = ["A", "B", "C", "D", "E"]
    c.add_column("Label", StringColumn(None, "Label", None, values=strs))
    
    c.metadata["date"] = ["2023-01-01"] * 5
    
    return c

def test_interpolate_linear():
    c = create_test_collection()
    
    # New X: 5, 15, 25, 35
    x_new = [5.0, 15.0, 25.0, 35.0]
    
    res = c.ops.interpolate(x_values=x_new)
    
    assert len(res) == 4
    np.testing.assert_array_almost_equal(res.step.values, x_new)
    
    # Expected Val: 50, 150, 250, 350
    expected_val = [50.0, 150.0, 250.0, 350.0]
    np.testing.assert_array_almost_equal(res["Val"].values, expected_val)
    
    # Label should be nearest.
    # 5 -> 0(A) or 10(B)? midpoint. verify behavior.
    # 5 is exactly between 0 and 10.
    # np.interp/searchsorted might pick one. usually left or right.
    # Let's see implemented behavior.
    # 15 -> 10(B) or 20(C)
    pass 

def test_interpolate_extrapolation():
    c = create_test_collection()
    
    # New X: -10, 50
    x_new = [-10.0, 50.0]
    
    res = c.ops.interpolate(x_values=x_new)
    
    # Linear extrapolation
    # -10 -> -100 (slope 10)
    # 50 -> 500
    expected_val = [-100.0, 500.0]
    np.testing.assert_array_almost_equal(res["Val"].values, expected_val)

def test_interpolate_point_count():
    c = create_test_collection()
    # 0 to 40, count=5 -> same as original
    res = c.ops.interpolate(point_count=5)
    np.testing.assert_array_almost_equal(res["Val"].values, c["Val"].values)
    
    # count=9 -> 0, 5, 10, ...
    res2 = c.ops.interpolate(point_count=9)
    assert len(res2) == 9
    assert res2.step.values[1] == 5.0
    assert res2["Val"].values[1] == 50.0

if __name__ == "__main__":
    test_interpolate_linear()
    test_interpolate_extrapolation()
    test_interpolate_point_count()
    print("All tests passed!")
