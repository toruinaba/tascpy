
import sys
import os
import numpy as np
import pytest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step
import tascpy.operations.core.combine # Register operations

def create_test_collection():
    c = ColumnCollection(step=[], columns={})
    c.step = Step(values=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    
    # Col A: [0, 10, 20, ..., 90]
    vals_a = [float(i*10) for i in range(10)]
    c.add_column("A", NumberColumn(None, "A", "unitA", values=vals_a))
    
    # Col B: [0, 2, 4, ..., 18]
    vals_b = [float(i*2) for i in range(10)]
    c.add_column("B", NumberColumn(None, "B", "unitB", values=vals_b))

    # Col C: [0, -10, -20, ..., -90]
    vals_c = [float(i*-10) for i in range(10)]
    c.add_column("C", NumberColumn(None, "C", "unitC", values=vals_c))
    
    return c

def test_sum_columns():
    c = create_test_collection()
    # Sum A and B -> [0, 12, 24, ..., 108]
    res = c.ops.sum_columns(columns=["A", "B"], result_column="SumAB")
    
    assert "SumAB" in res.columns
    expected = np.array([float(i*12) for i in range(10)])
    np.testing.assert_array_almost_equal(res["SumAB"].values, expected)
    print("Pass: sum_columns")

def test_average_columns():
    c = create_test_collection()
    # Avg A and B -> (10x + 2x)/2 = 6x -> [0, 6, 12, ..., 54]
    res = c.ops.average_columns(columns=["A", "B"], result_column="AvgAB")
    
    assert "AvgAB" in res.columns
    expected = np.array([float(i*6) for i in range(10)])
    np.testing.assert_array_almost_equal(res["AvgAB"].values, expected)
    print("Pass: average_columns")

def test_conditional_select():
    c = create_test_collection()
    # If A > 40 (indices 5,6,7,8,9), select B, else select C
    # Indices 0-4 (A<=40): C -> 0, -10, -20, -30, -40
    # Indices 5-9 (A>40): B -> 10, 12, 14, 16, 18
    
    # inject_columns(num_inputs=3) -> expects 3 positional args for v1, v2, cond_values
    res = c.ops.conditional_select(
        "B", "C", "A",
        threshold=40.0, compare=">",
        result_column="Select"
    )
    
    expected = [0.0, -10.0, -20.0, -30.0, -40.0, 10.0, 12.0, 14.0, 16.0, 18.0]
    np.testing.assert_array_almost_equal(res["Select"].values, expected)
    print("Pass: conditional_select")

def test_custom_combine():
    c = create_test_collection()
    # A + B using custom func
    def add_func(a, b):
        return a + b
        
    # inject_columns(num_inputs=2) -> v1, v2
    res = c.ops.custom_combine("A", "B", combine_func=add_func, result_column="CustomSum")
    expected = np.array([float(i*12) for i in range(10)])
    np.testing.assert_array_almost_equal(res["CustomSum"].values, expected)
    print("Pass: custom_combine")

def test_switch_by_step():
    c = create_test_collection()
    # Step at 4.5. Before (<4.5, indices 0-4): A. After (>=4.5, indices 5-9): B.
    # A: 0, 10, 20, 30, 40
    # B: 10, 12, 14, 16, 18 (indices 5-9 -> 5*2=10... wait. B is i*2. Index 5 is 10. Correct)
    
    # inject_columns(num_inputs=2, include_step=True) -> step (auto), v1, v2
    res = c.ops.switch_by_step(
        "A", "B", threshold=4.5, by_step_value=True, result_column="Switch"
    )
    
    expected = [0.0, 10.0, 20.0, 30.0, 40.0, 10.0, 12.0, 14.0, 16.0, 18.0]
    np.testing.assert_array_almost_equal(res["Switch"].values, expected)
    print("Pass: switch_by_step")

def test_blend_by_step():
    c = create_test_collection()
    # Step: 0..9. A: 0..90. B: 0..18.
    # Blend from 4 to 6.
    # <=4: A. >=6: B.
    # 5: Midpoint (linear). A(50), B(10). Mid = 30?
    
    # inject_columns(num_inputs=2, include_step=True) -> step (auto), v1, v2
    res = c.ops.blend_by_step(
        "A", "B", start=4.0, end=6.0, by_step_value=True, result_column="Blend"
    )
    
    # 0,1,2,3,4 -> A -> 0,10,20,30,40
    # 6,7,8,9 -> B -> 12,14,16,18
    # 5 -> (5 - 4)/(6-4) = 0.5. A(50)*0.5 + B(10)*0.5 = 25 + 5 = 30.
    
    expected = [0.0, 10.0, 20.0, 30.0, 40.0, 30.0, 12.0, 14.0, 16.0, 18.0]
    np.testing.assert_array_almost_equal(res["Blend"].values, expected)
    print("Pass: blend_by_step")

if __name__ == "__main__":
    test_sum_columns()
    test_average_columns()
    test_conditional_select()
    test_custom_combine()
    test_switch_by_step()
    test_blend_by_step()
