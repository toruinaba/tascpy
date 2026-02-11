import sys
from pathlib import Path
import numpy as np
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.column import Column, NumberColumn, StringColumn
from tascpy.core.step import Step
from tascpy.core.collection import ColumnCollection

def test_step_find_nearest():
    print("\n[1] Testing Step.find_nearest_index")
    s = Step([0, 10, 20, 30, 40])
    
    idx = s.find_nearest_index(12)
    print(f"Nearest to 12: index={idx}, value={s.values[idx]}")
    assert idx == 1  # 10 is nearest

    idx = s.find_nearest_index(28)
    print(f"Nearest to 28: index={idx}, value={s.values[idx]}")
    assert idx == 3  # 30 is nearest

    # Test with empty step
    s_empty = Step([])
    assert s_empty.find_nearest_index(10) == -1
    print("Empty step check passed")

def test_column_stats():
    print("\n[2] Testing Column Statistics (ptp, abs_max)")
    data = [1.0, -5.0, 3.0, None, 2.0]
    col = NumberColumn(None, "test", None, data)
    
    ptp = col.ptp()
    print(f"PTP (1.0, -5.0, 3.0, 2.0): {ptp}")
    assert ptp == 8.0  # 3.0 - (-5.0) = 8.0

    abs_max = col.abs_max()
    print(f"Abs Max: {abs_max}")
    assert abs_max == 5.0  # |-5.0| = 5.0

    # Test with all None
    col_none = NumberColumn(None, "none", None, [None, None])
    assert col_none.ptp() is None
    print("All None check passed")

def test_column_validation():
    print("\n[3] Testing Column Validation (valid/invalid index)")
    # data: [0: 1.0, 1: None, 2: 3.0, 3: "error"] -> mixed type loading
    values = [1.0, None, 3.0, "error"]
    col = Column(None, "mixed", None, values)
    
    print(f"Values: {col.values}")
    
    n_valid = col.n_valid
    print(f"n_valid: {n_valid}")
    assert n_valid == 3 # 1.0, 3.0, "error" are not None

    # is_valid (None check)
    valid_mask = col.is_valid()
    print(f"is_valid: {valid_mask}")
    assert valid_mask[1] == False
    assert valid_mask[0] == True
    
    # first_valid_index
    idx = col.first_valid_index
    print(f"first_valid_index: {idx}")
    assert idx == 0

    # first_invalid_index (None check in normal Column)
    inv_idx = col.first_invalid_index
    print(f"first_invalid_index (for None): {inv_idx}")
    assert inv_idx == 1

def test_to_numeric_and_invalid_detection():
    print("\n[4] Testing to_numeric and Invalid Detection")
    values = [1.0, 2.0, "error", 4.0, None]
    col = Column(None, "raw", None, values) # Mixed type
    
    print("Converting with errors='coerce'...")
    num_col = col.to_numeric(errors='coerce')
    
    print(f"Converted values: {num_col.values}")
    # "error" should become NaN, None should become NaN
    
    # Check "error" index (2)
    assert np.isnan(num_col.values[2])
    # Check None index (4)
    assert np.isnan(num_col.values[4])
    
    # Now check first_invalid_index on NumberColumn (checks for NaN)
    first_nan = num_col.first_invalid_index
    print(f"First Invalid (NaN) Index: {first_nan}")
    assert first_nan == 2  # "error" -> NaN was at index 2

def test_collection_wrappers():
    print("\n[5] Testing ColumnCollection Wrappers")
    step = Step([1, 2, 3, 4])
    c1 = NumberColumn(None, "c1", None, [10, 20, 30, 40])
    c2 = Column(None, "c2", None, ["a", "b", "c", "d"])
    col = ColumnCollection(step, {"c1": c1, "c2": c2})

    # find_nearest_step
    idx, val = col.find_nearest_step(2.8)
    print(f"Nearest step to 2.8: {val} at {idx}")
    assert idx == 2 # 3 is nearest
    assert val == 3

    # max
    maxs = col.max()
    print(f"Maxs: {maxs}")
    assert maxs["c1"] == 40
    
    # to_numeric
    # c2 cannot be converted, let's see errors='coerce'
    c2_values = ["1.1", "2.2", "invalid", "4.4"]
    col.columns["c2"] = Column(None, "c2", None, c2_values)
    
    num_col = col.to_numeric(errors='coerce')
    print(f"Converted Collection c2: {num_col.columns['c2'].values}")
    assert np.isnan(num_col.columns["c2"].values[2])

if __name__ == "__main__":
    try:
        test_step_find_nearest()
        test_column_stats()
        test_column_validation()
        test_to_numeric_and_invalid_detection()
        test_collection_wrappers()
        print("\n\033[92mALL TESTS PASSED\033[0m")
    except AssertionError as e:
        print(f"\n\033[91mTEST FAILED: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n\033[91mERROR: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
