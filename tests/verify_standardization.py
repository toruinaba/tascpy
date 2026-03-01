import sys
from pathlib import Path
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.collection import ColumnCollection
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection

# Import modules to register operations
import tascpy.analytics.operations.coordinate.distance
import tascpy.analytics.operations.coordinate.interpolation
import tascpy.analytics.operations.core.stats
import tascpy.analytics.operations.core.filters
import tascpy.analytics.operations.load_displacement.analysis

def test_standardization():
    print("Testing Operation Standardization (Aliases)...")
    
    # 1. Coordinate Aliases
    print("\n[1] Testing Coordinate Aliases")
    try:
        from tascpy.analytics.operations.coordinate.distance import distance, nearest_neighbors, cluster
        from tascpy.analytics.operations.coordinate.interpolation import interp_point, interp_grid
        
        print("SUCCESS: Imported coordinate aliases (distance, nearest_neighbors, cluster, interp_point, interp_grid)")
        
        # Test functionality
        col = CoordinateCollection(columns={}, step=[1, 2])
        col.add_column("p1", [0, 0])
        col.columns["p1"].metadata = {"coordinates": {"x": 0, "y": 0}}
        col.add_column("p2", [3, 4])
        col.columns["p2"].metadata = {"coordinates": {"x": 3, "y": 4}}
        
        d = distance(col, "p1", "p2")
        print(f"distance(p1, p2) = {d}")
        if abs(d - 5.0) < 1e-6:
             print("SUCCESS: distance alias works correctly")
        
    except Exception as e:
        print(f"ERROR: Coordinate aliases failed: {e}")
        import traceback
        traceback.print_exc()

    # 2. Core Aliases
    print("\n[2] Testing Core Aliases")
    try:
        from tascpy.analytics.operations.core.stats import ma, outliers
        from tascpy.analytics.operations.core.filters import filter_val, filter_cond, rm_outliers
        
        print("SUCCESS: Imported core aliases (ma, outliers, filter_val, filter_cond, rm_outliers)")
        
        col = ColumnCollection(columns={}, step=list(range(10)))
        col.add_column("val", list(range(10)))
        
        # Test filter_val
        res = filter_val(col, "val", 5)
        if len(res["val"].values) == 1 and res["val"].values[0] == 5:
            print("SUCCESS: filter_val alias works correctly")
            
    except Exception as e:
        print(f"ERROR: Core aliases failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. Load Displacement Aliases
    print("\n[3] Testing Load Displacement Aliases")
    try:
        from tascpy.analytics.operations.load_displacement.analysis import stiffness, yield_point
        # Note: 'energy' alias was skipped as calculate_energy was missing
        
        print("SUCCESS: Imported load_displacement aliases (stiffness, yield_point)")
        
        # Create dummy LD data with more points
        ld_col = LoadDisplacementCollection(columns={}, step=list(range(10)))
        ld_col.add_column("displacement", [i * 0.5 for i in range(10)])
        ld_col.columns["displacement"].unit = "mm"
        ld_col.add_column("load", [i * 5.0 for i in range(10)]) # Linear 5N/mm
        ld_col.columns["load"].unit = "N"
        
        k = stiffness(ld_col, range_start=0.1, range_end=0.9)
        print(f"stiffness = {k}")
        if k > 0:
             print("SUCCESS: stiffness alias works correctly")

    except Exception as e:
        print(f"ERROR: Load Displacement aliases failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_standardization()
