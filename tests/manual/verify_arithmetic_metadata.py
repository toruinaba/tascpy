import sys
from pathlib import Path
import pytest
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.step import Step
from tascpy.core.collection import ColumnCollection
from tascpy.analytics.operations.proxy import CollectionOperations

def test_arithmetic_metadata():
    print("\n[1] Preparing Data")
    step = Step([1, 2, 3])
    data = {
        "A": [10, 20, 30],
        "B": [1, 2, 3],
        "X": [0.1, 0.2, 0.3],
        "Y": [1.0, 4.0, 9.0]
    }
    # Initial metadata
    col = ColumnCollection(step, data)
    col["A"].unit = "m"
    col["A"].ch = "CH1"
    col["B"].unit = "s"
    col["B"].ch = "CH2"
    col["X"].unit = "s"
    col["Y"].unit = "m"
    
    # 1. Test Add with metadata
    print("\n[2] Testing Add with metadata")
    res1 = col.ops.add("A", "B", unit="m/s_custom", ch="CH_NEW").end()
    res_col = res1["A+B"]
    print(f"Add Result: Unit={res_col.unit}, Ch={res_col.ch}")
    assert res_col.unit == "m/s_custom"
    assert res_col.ch == "CH_NEW"
    
    # Test Add default (should inherit from A)
    res1_def = col.ops.add("A", "B", result_column="A+B_def").end()
    print(f"Add Default: Unit={res1_def['A+B_def'].unit}, Ch={res1_def['A+B_def'].ch}")
    assert res1_def['A+B_def'].unit == "m"
    assert res1_def['A+B_def'].ch is None  # Default is None for new columns unless set?
    # Note: original add impl: detect_column_type(None, ...) -> ch is None. 
    # But wait, original add implementation:
    # "original_column = collection[column1]"
    # "unit = original_column.unit ..."
    # "column = detect_column_type(None, result_column, unit, ...)"
    # So ch was explicitly None in original.
    
    # 2. Test Multiply with metadata
    print("\n[3] Testing Multiply with metadata")
    res2 = col.ops.multiply("A", "B", unit="m*s", ch="CH_MUL").end()
    res_col = res2["A*B"]
    print(f"Mul Result: Unit={res_col.unit}, Ch={res_col.ch}")
    assert res_col.unit == "m*s"
    assert res_col.ch == "CH_MUL"
    
    # 3. Test Evaluate with metadata
    print("\n[4] Testing Evaluate with metadata")
    res3 = col.ops.evaluate("A + B * 2", result_column="eval_res", unit="mixed", ch="CH_EVAL").end()
    res_col = res3["eval_res"]
    print(f"Eval Result: Unit={res_col.unit}, Ch={res_col.ch}")
    assert res_col.unit == "mixed"
    assert res_col.ch == "CH_EVAL"
    
    # 4. Test Diff with metadata
    print("\n[5] Testing Diff with metadata")
    # Default diff unit: m / s
    res4_def = col.ops.diff("Y", "X").end()
    print(f"Diff Default: Unit={res4_def['d(Y)/d(X)'].unit}")
    assert res4_def['d(Y)/d(X)'].unit == "m/s"
    
    # Custom diff unit
    res4 = col.ops.diff("Y", "X", unit="speed", ch="CH_DIFF").end()
    print(f"Diff Custom: Unit={res4['d(Y)/d(X)'].unit}, Ch={res4['d(Y)/d(X)'].ch}")
    assert res4['d(Y)/d(X)'].unit == "speed"
    assert res4['d(Y)/d(X)'].ch == "CH_DIFF"
    
    # 5. Test Integrate with metadata
    print("\n[6] Testing Integrate with metadata")
    # Custom integrate unit
    res5 = col.ops.integrate("Y", "X", unit="area", ch="CH_INT").end()
    res_col = res5[f"∫Y·dX"]  # Actual column name format needs check
    # math.py: f"∫{y_column}·d{x_column}"
    print(f"Int Custom: Unit={res_col.unit}, Ch={res_col.ch}")
    assert res_col.unit == "area"
    assert res_col.ch == "CH_INT"

    print("Metadata Handling Passed")

if __name__ == "__main__":
    try:
        test_arithmetic_metadata()
        print("\n\033[92mALL TESTS PASSED\033[0m")
    except Exception as e:
        print(f"\n\033[91mTEST FAILED: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
