
import sys
import os
import numpy as np
import pytest

# Apply path trick
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step
from tascpy.operations.core.select import select, fetch_near_step

def create_test_collection():
    # Steps: 0.0, 0.1, 0.2, ... 0.9
    steps = [0.1 * i for i in range(10)]
    # A: 0, 1, ... 9
    col_a_vals = [float(i) for i in range(10)]
    # B: 10, 11, ... 19
    col_b_vals = [float(i + 10) for i in range(10)]
    
    coll = ColumnCollection(step=Step(values=steps), columns={})
    coll.add_column("A", NumberColumn("CH1", "A", "N", col_a_vals))
    coll.add_column("B", NumberColumn("CH2", "B", "mm", col_b_vals))
    return coll

def test_select_by_indices():
    c = create_test_collection()
    # Select indices 1, 3, 5
    res = select(c, indices=[1, 3, 5])
    
    assert len(res) == 3
    assert np.isclose(res.step.values[0], 0.1)
    assert np.isclose(res.step.values[1], 0.3)
    assert np.isclose(res.step.values[2], 0.5)
    assert res["A"].values[0] == 1.0
    assert res["A"].values[1] == 3.0
    print("Pass: select_by_indices")

def test_select_by_steps_value():
    c = create_test_collection()
    # Select steps 0.2, 0.5, 0.8
    # Using tolerance is prudent for floats, but default exists?
    # Default tolerance in step.find_step_index is None -> strict equality?
    # select() implementation passes tolerance.
    
    # 0.1 * 2 = 0.2. In float 0.2 is 0.2.
    res = select(c, steps=[0.2, 0.5, 0.8], by_step_value=True, tolerance=1e-9)
    
    assert len(res) == 3
    assert np.isclose(res.step.values[0], 0.2)
    assert np.isclose(res["A"].values[0], 2.0)
    print("Pass: select_by_steps_value")

def test_select_by_steps_index_mode():
    c = create_test_collection()
    # select with steps=[1, 4], by_step_value=False -> indices 1, 4
    res = select(c, steps=[1, 4], by_step_value=False)
    
    assert len(res) == 2
    assert np.isclose(res.step.values[0], 0.1) # Index 1
    assert np.isclose(res.step.values[1], 0.4) # Index 4
    print("Pass: select_by_steps_index_mode")

def test_select_columns_subset():
    c = create_test_collection()
    # Filter only column A
    res = select(c, columns=["A"], indices=[0, 1])
    
    assert "A" in res.columns
    assert "B" not in res.columns
    assert len(res) == 2
    print("Pass: select_columns_subset")

def test_fetch_near_step():
    c = create_test_collection()
    # Step closest to 0.42 -> 0.4
    # fetch_near_step returns INDICES via @filter_rows? No, it returns ColumnCollection if fully decorated.
    # Original signature hints List[int], but decorated returns Collection.
    # wait, fetch_near_step logic is "find nearest index".
    # Implementation: returns [int(idx)].
    # @filter_rows uses this to filtering.
    
    res = fetch_near_step(c, 0.42)
    assert len(res) == 1
    assert np.isclose(res.step.values[0], 0.4)
    print("Pass: fetch_near_step")
    
if __name__ == "__main__":
    test_select_by_indices()
    test_select_by_steps_value()
    test_select_by_steps_index_mode()
    test_select_columns_subset()
    test_fetch_near_step()
