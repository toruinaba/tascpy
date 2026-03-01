
import sys
import os
import numpy as np

# Apply path trick
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column, NumberColumn
from tascpy.core.step import Step
from tascpy.analytics.operations.core.select import select, fetch_near_step

def test_select_abstraction():
    print("Testing Select Abstraction...")
    
    # Setup data
    steps = [0.0, 0.1, 0.2, 0.3, 0.4]
    col_a_vals = [10, 20, 30, 40, 50]
    col_b_vals = [100, 200, 300, 400, 500]
    
    col_a = NumberColumn(ch="CH1", name="A", unit="N", values=col_a_vals)
    col_b = NumberColumn(ch="CH2", name="B", unit="mm", values=col_b_vals)
    
    # Initialize with step and empty columns dict if needed
    coll = ColumnCollection(step=Step(values=steps), columns={})
    coll.add_column("A", col_a)
    coll.add_column("B", col_b)
    
    print("[1] Testing Select by Indices")
    # Select indices [1, 3] -> steps 0.1, 0.3
    res1 = select(coll, indices=[1, 3])
    
    assert len(res1) == 2
    # Convert to list for safe comparison if it's an array
    res1_steps = res1.step.values.tolist() if isinstance(res1.step.values, np.ndarray) else res1.step.values
    assert res1_steps == [0.1, 0.3]
    
    res1_a = res1["A"].values.tolist() if isinstance(res1["A"].values, np.ndarray) else res1["A"].values
    assert res1_a == [20, 40]
    print("  Pass: Indices selection")
    
    print("[2] Testing Select by Steps")
    # Select steps [0.2, 0.4]
    res2 = select(coll, steps=[0.2, 0.4], by_step_value=True)
    
    assert len(res2) == 2
    # Tolerance might be needed for float comparison but simple values should match
    res2_steps = res2.step.values.tolist() if isinstance(res2.step.values, np.ndarray) else res2.step.values
    assert np.allclose(res2_steps, [0.2, 0.4])
    
    res2_b = res2["B"].values.tolist() if isinstance(res2["B"].values, np.ndarray) else res2["B"].values
    assert res2_b == [300, 500]
    print("  Pass: Step value selection")
    
    print("[3] Testing Column Filtering")
    # Select only column "A" and index [0]
    res3 = select(coll, columns=["A"], indices=[0])
    
    assert "A" in res3.columns
    assert "B" not in res3.columns
    assert len(res3) == 1
    result_a = res3["A"].values.tolist() if isinstance(res3["A"].values, np.ndarray) else res3["A"].values
    assert result_a == [10]
    print("  Pass: Column filtering")
    
    print("[4] Testing Fetch Near Step")
    # Fetch near A=32 (closest is 30 at index 2)
    res4 = fetch_near_step(coll, "A", 32)
    
    assert len(res4) == 1
    res4_steps = res4.step.values.tolist() if isinstance(res4.step.values, np.ndarray) else res4.step.values
    res4_a = res4["A"].values.tolist() if isinstance(res4["A"].values, np.ndarray) else res4["A"].values
    assert res4_steps == [0.2]
    assert res4_a == [30]
    print("  Pass: Fetch near step")

    print("[5] Testing Empty Selection")
    res5 = select(coll, indices=[])
    assert len(res5) == 0
    assert len(res5["A"].values) == 0
    print("  Pass: Empty selection")
    
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_select_abstraction()
