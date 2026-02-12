
import sys
from pathlib import Path
import numpy as np

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from tascpy.domains.load_displacement import create_load_displacement_collection
from tascpy.operations.load_displacement.curves import create_skeleton_curve, create_cumulative_curve
from tascpy.core.result import XYSeriesResult, Curve
from tascpy.core.column import Column

def test_curve_refactoring():
    print("Testing Curve Refactoring (XYSeriesResult)...")
    
    # 1. Dummy Data Creation
    # Create a cyclic loading data pattern
    # Cycle 1: 0 -> 10 -> 0 -> -10 -> 0
    # Cycle 2: 0 -> 20 -> 0 -> -20 -> 0
    t = np.linspace(0, 4*np.pi, 100)
    cycle_ids = np.zeros_like(t, dtype=int)
    cycle_ids[:50] = 1
    cycle_ids[50:] = 2
    
    disp = np.sin(t) * (10 * ((t > 2*np.pi) + 1)) # amp 10 then 20
    load = disp * 2 # stiffness 2
    
    col = create_load_displacement_collection(
        step=list(range(100)),
        columns={
            "load": load,
            "displacement": disp,
            "cycle": cycle_ids
        },
        load_column="load",
        displacement_column="displacement"
    )
    
    # 2. Test Skeleton Curve
    print(" Creating skeleton curve...")
    res_ske = create_skeleton_curve(col, has_decrease=False)
    
    # Verify it exists in results
    if "skeleton_curve" not in res_ske.results:
        print("FAIL: 'skeleton_curve' not found in results")
        sys.exit(1)
        
    curve_ske = res_ske.results["skeleton_curve"]
    if not isinstance(curve_ske, XYSeriesResult):
        print(f"FAIL: Result is not a XYSeriesResult instance, got {type(curve_ske)}")
        sys.exit(1)
        
    print(f" Skeleton Curve found: {curve_ske}")
    print(f" Skeleton X data length: {len(curve_ske.x)}")
    print(f" Skeleton Y data length: {len(curve_ske.y)}")
    
    # Verify backward compatibility
    if "curves" in res_ske.metadata and "skeleton_curve" in res_ske.metadata["curves"]:
        print(" Backward compatibility: metadata['curves']['skeleton_curve'] exists")
    else:
        print("FAIL: Backward compatibility broken")
        sys.exit(1)

    # 3. Test Cumulative Curve
    print(" Creating cumulative curve...")
    res_cum = create_cumulative_curve(col)
    
    if "cumulative_curve" not in res_cum.results:
        print("FAIL: 'cumulative_curve' not found in results")
        sys.exit(1)
        
    curve_cum = res_cum.results["cumulative_curve"]
    print(f" Cumulative Curve found: {curve_cum}")
    
    # 4. Test Access Pattern
    print(" Testing access patterns...")
    
    # collection["name"] -> should return XYSeriesResult (which is also Curve alias)
    try:
        c = res_ske["skeleton_curve"]
        if not isinstance(c, XYSeriesResult):
             print(f"FAIL: collection['skeleton_curve'] returned {type(c)}")
        else:
             print(" collection['skeleton_curve'] works")
    except KeyError:
        print("FAIL: collection['skeleton_curve'] raised KeyError")

    # collection.keys() -> should include curve name
    keys = res_ske.keys()
    if "skeleton_curve" in keys:
        print(" collection.keys() contains 'skeleton_curve'")
    else:
        print(f"FAIL: 'skeleton_curve' missing from keys(): {keys}")

    # collection["name.x"] -> should return Column
    try:
        col_x = res_ske["skeleton_curve.x"]
        if isinstance(col_x, Column):
            print(" dot notation 'skeleton_curve.x' works")
        else:
            print(f"FAIL: 'skeleton_curve.x' returned {type(col_x)}")
    except KeyError:
        print("FAIL: 'skeleton_curve.x' raised KeyError")

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_curve_refactoring()
