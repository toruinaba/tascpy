import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.collection import ColumnCollection
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.analytics.operations.validation import requires_domain, requires_coordinates

def test_coordinate_validation():
    print("Testing coordinate validation...")
    
    # 1. Test requires_domain failure
    print("\n[1] Testing requires_domain failure")
    col = ColumnCollection(step=[1, 2], columns={"A": [1, 2]})
    try:
        from tascpy.analytics.operations.coordinate.basic import get_column_coordinates
        get_column_coordinates(col, "A")
        print("ERROR: Should have failed domain check")
    except ValueError as e:
        print(f"SUCCESS: Caught domain error: {e}")

    # 2. Test requires_coordinates failure (empty coordinates)
    print("\n[2] Testing requires_coordinates failure")
    coord_col = CoordinateCollection(step=[1, 2], columns={"A": [1, 2]})
    # "A" has no coordinates yet
    
    try:
        from tascpy.analytics.operations.coordinate.distance import find_nearest_neighbors
        find_nearest_neighbors(coord_col, "A")
        print("ERROR: Should have failed coordinate check")
    except ValueError as e:
        print(f"SUCCESS: Caught coordinate error: {e}")
        
    # 3. Test success case
    print("\n[3] Testing success case")
    coord_col.set_column_coordinates("A", x=0, y=0)
    coord_col.add_column("B", [3, 4])
    coord_col.set_column_coordinates("B", x=3, y=4)
    
    try:
        from tascpy.analytics.operations.coordinate.distance import find_nearest_neighbors
        find_nearest_neighbors(coord_col, "A", n_neighbors=1)
        print("SUCCESS: find_nearest_neighbors executed")
    except Exception as e:
        print(f"ERROR: Failed valid operation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_coordinate_validation()
