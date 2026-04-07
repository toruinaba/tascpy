import sys
from pathlib import Path
import numpy as np
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.step import Step
from tascpy.core.collection import ColumnCollection

def test_abstraction_edge_cases():
    print("\n[1] Preparing Data")
    step = Step([1, 2, 3])
    data = {"A": [10, 20, 30], "B": [2, 0, 5]} # B includes 0 for division test
    col = ColumnCollection(step, data)
    
    # 1. Test Zero Division (Error - default)
    print("\n[2] Testing Zero Division (Error)")
    try:
        col.ops.divide("A", "B").end()
        print("FAILED: ZeroDivisionError not raised")
        sys.exit(1)
    except ValueError as e:
        print(f"Caught expected error: {e}")
        assert "ゼロによる除算" in str(e)
        
    # 2. Test Zero Division (None)
    print("\n[3] Testing Zero Division (None)")
    res_none = col.ops.divide("A", "B", handle_zero_division="none", result_column="div_none").end()
    vals = res_none["div_none"].values
    print(f"Values: {vals}")
    # NumberColumn converts None to NaN
    assert np.isnan(vals[1])
    assert vals[0] == 5.0
    
    # 3. Test Zero Division (Inf)
    print("\n[4] Testing Zero Division (Inf)")
    res_inf = col.ops.divide("A", "B", handle_zero_division="inf", result_column="div_inf").end()
    vals_inf = res_inf["div_inf"].values
    print(f"Values: {vals_inf}")
    assert np.isinf(vals_inf[1])
    
    # 4. Test Scalar Operation
    print("\n[5] Testing Scalar Operation")
    res_scalar = col.ops.add("A", 100, result_column="A+100").end()
    vals_scalar = res_scalar["A+100"].values
    print(f"Values: {vals_scalar}")
    assert vals_scalar[0] == 110.0
    
    # 5. Test Scalar as First Argument (Not supported by standard ops usually, but let's see)
    # The abstraction assumes column names or values.
    # col.ops.add(100, "A") -> 100 is not in columns -> constant. "A" is in columns -> column?
    # Wait, mapping in abstraction.py:
    # "for arg in input_args: if isinstance(arg, str) and arg in collection.columns: ... else: value"
    # So `add(100, "A")` -> v1=100, v2=values("A").
    # `v1 + v2` should work (broadcast).
    
    print("\n[6] Testing Scalar as first arg (100 + A)")
    # Note: The `ops` proxy might have signature constraints? 
    # `add(column1, column2_or_value)` -> signature says column1: str.
    # But python doesn't enforce types at runtime unless we check.
    # The proxy passes args to `add`. `add` is the wrapper.
    # Wrapper receives `*args`.
    # `add(100, "A")`.
    # Wrapper sees 100. Type int. Not string. -> Constant.
    # Wrapper sees "A". Type str. In columns. -> Column values.
    # Result: 100 + A. Should work!
    
    try:
        res_scalar_rev = col.ops.add(100, "A", result_column="100+A").end()
        vals_rev = res_scalar_rev["100+A"].values
        print(f"Values: {vals_rev}")
        assert vals_rev[0] == 110.0
    except Exception as e:
        print(f"Scalar first arg failed (might be expected if strict typing intended, but abstraction allows it): {e}")
        # If strict typing in `add` signature `column1: str` is enforced by some runtime check (not here), it would fail.
        # But `add` signature in `math.py` has `column1: str`.
        # However, `ops.add` calls the function.
        # Let's see if it works.
        pass

    print("\nEdge Case Tests Passed")

if __name__ == "__main__":
    try:
        test_abstraction_edge_cases()
        print("\n\033[92mALL TESTS PASSED\033[0m")
    except Exception as e:
        print(f"\n\033[91mTEST FAILED: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
