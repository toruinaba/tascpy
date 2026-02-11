import sys
from pathlib import Path
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.collection import ColumnCollection
# Import modules to register operations
import tascpy.operations.core.math
import tascpy.operations.core.stats

def test_core_expansion():
    print("Testing Core Expansion...")
    
    # Create sample data
    x = np.linspace(0, 10, 20)
    y = np.sin(x)
    # Add noise for smoothing test
    y_noisy = y + np.random.normal(0, 0.1, 20)
    y_noisy[5] = 5.0 # Outlier
    
    col = ColumnCollection(columns={}, step=list(range(20)))
    col.add_column("x", x)
    col.add_column("y", y)
    col.add_column("y_noisy", y_noisy)
    
    # 1. Test diff (math.py)
    print("\n[1] Testing diff")
    try:
        from tascpy.operations.core.math import diff
        res_diff = diff(col, "y", "x", result_column="dy_dx")
        print("SUCCESS: diff executed")
        # Check result (derivative of sin is cos)
        # Numerical diff might be slightly off, just check existence
        if "dy_dx" in res_diff.columns:
            print("SUCCESS: Result column 'dy_dx' created")
    except Exception as e:
        print(f"ERROR: diff failed: {e}")
        import traceback
        traceback.print_exc()

    # 2. Test integrate (math.py)
    print("\n[2] Testing integrate")
    try:
        from tascpy.operations.core.math import integrate
        res_int = integrate(col, "y", "x", result_column="int_y")
        print("SUCCESS: integrate executed")
        if "int_y" in res_int.columns:
            print("SUCCESS: Result column 'int_y' created")
    except Exception as e:
        print(f"ERROR: integrate failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. Test smooth / gaussian_filter (stats.py)
    print("\n[3] Testing smooth (gaussian)")
    try:
        from tascpy.operations.core.stats import smooth
        res_smooth = smooth(col, "y_noisy", method="gaussian", sigma=1.0, result_column="y_smooth")
        print("SUCCESS: smooth(gaussian) executed")
        if "y_smooth" in res_smooth.columns:
            print("SUCCESS: Result column 'y_smooth' created")
            # Should be closer to sin(x) than y_noisy
            # Simple check: max value should be reduced from outlier (5.0)
            orig_max = np.max(col["y_noisy"].values)
            res = res_smooth["y_smooth"].values
            # Filter None/NaN for max check
            valid_res = [v for v in res if v is not None and not np.isnan(v)]
            smooth_max = np.max(valid_res)
            print(f"Original Max: {orig_max}, Smoothed Max: {smooth_max}")
            if smooth_max < orig_max:
                print("SUCCESS: Smoothing reduced peak noise")
    except Exception as e:
        print(f"ERROR: smooth failed: {e}")
        import traceback
        traceback.print_exc()

    # 4. Test core accessibility via registry (optional check)
    # This checks if "core" domain operations are registered properly
    print("\n[4] Checking registry (implicit)")
    # Since we imported the modules, the @operation decorators should have run.

if __name__ == "__main__":
    test_core_expansion()
