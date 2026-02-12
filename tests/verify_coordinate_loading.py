import sys
from pathlib import Path
import pytest
import json
import csv
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.step import Step
from tascpy.core.collection import ColumnCollection
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.operations.proxy import CollectionOperations

def test_coordinate_loading():
    print("\n[1] Preparing Data")
    step = Step([1, 2, 3])
    data = {"col_A": [1, 1, 1], "col_B": [2, 2, 2]}
    col = ColumnCollection(step, data)
    
    # 1. JSON Loading
    print("\n[2] Testing JSON Loading")
    json_path = Path("temp_coords.json")
    json_data = {
        "col_A": {"x": 10.0, "y": 20.0, "z": 30.0},
        "col_B": {"x": 5.0, "y": 5.0} # No Z
    }
    with open(json_path, "w") as f:
        json.dump(json_data, f)
        
    try:
        coord_col = col.ops.as_domain("coordinate", coordinates=str(json_path)).end()
        
        # Verify col_A
        xa, ya, za = coord_col.get_column_coordinates("col_A")
        print(f"col_A coords: {xa}, {ya}, {za}")
        assert xa == 10.0 and ya == 20.0 and za == 30.0
        
        # Verify col_B
        xb, yb, zb = coord_col.get_column_coordinates("col_B")
        print(f"col_B coords: {xb}, {yb}, {zb}")
        assert xb == 5.0 and yb == 5.0 and zb is None
        
        print("JSON Loading Passed")
        
    finally:
        if json_path.exists():
            json_path.unlink()

    # 2. CSV Loading
    print("\n[3] Testing CSV Loading")
    csv_path = Path("temp_coords.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Column", "X", "Y", "Z"])
        writer.writerow(["col_A", "100", "200", "300"])
        writer.writerow(["col_B", "50", "50", ""]) # No Z
        
    try:
        coord_col = col.ops.as_domain("coordinate", coordinates=str(csv_path)).end()
        
        # Verify col_A
        xa, ya, za = coord_col.get_column_coordinates("col_A")
        print(f"col_A coords: {xa}, {ya}, {za}")
        assert xa == 100.0 and ya == 200.0 and za == 300.0
        
        # Verify col_B
        xb, yb, zb = coord_col.get_column_coordinates("col_B")
        print(f"col_B coords: {xb}, {yb}, {zb}")
        assert xb == 50.0 and yb == 50.0 and zb is None
        
        print("CSV Loading Passed")
        
    finally:
        if csv_path.exists():
            csv_path.unlink()
            
    # 3. Dict Loading (Regression Test)
    print("\n[4] Testing Dict Loading")
    dict_data = {"col_A": {"x": 1, "y": 1}}
    coord_col = col.ops.as_domain("coordinate", coordinates=dict_data).end()
    xa, _, _ = coord_col.get_column_coordinates("col_A")
    assert xa == 1
    print("Dict Loading Passed")


if __name__ == "__main__":
    try:
        test_coordinate_loading()
        print("\n\033[92mALL TESTS PASSED\033[0m")
    except Exception as e:
        print(f"\n\033[91mTEST FAILED: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
