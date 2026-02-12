
import sys
from pathlib import Path
import numpy as np

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from tascpy.domains.strain import create_strain_collection, StrainCollection
from tascpy.operations.strain.rosette import calculate_rosette_strains
from tascpy.operations.strain.visualization import plot_rosette_vectors

def test_strain_domain():
    print("Testing Strain Domain...")
    
    # 1. Create StrainCollection
    n_steps = 10
    steps = np.arange(n_steps)
    
    # Simulate a uniaxial stress state along X-axis
    # e1 = 1000 microstrain, e2 = -300 (Poisson 0.3)
    # Rotating this state by 0 degrees should give e_x=1000, e_y=-300
    # For a 0/45/90 rosette aligned with X-axis:
    # e_0 (0 deg) = e_x = 1000
    # e_90 (90 deg) = e_y = -300
    # e_45 (45 deg) = (e_x + e_y)/2 + (e_x - e_y)/2 * cos(90) + gamma_xy/2 * sin(90) -> (e_x+e_y)/2 + gamma_xy/2
    # If pure principal stress along X, shear gamma_xy = 0
    # So e_45 = (1000 - 300) / 2 = 350
    
    e_0 = np.full(n_steps, 1000.0)
    e_45 = np.full(n_steps, 350.0)
    e_90 = np.full(n_steps, -300.0)
    
    col = create_strain_collection(
        step=list(steps),
        columns={
            "sg1": e_0,
            "sg2": e_45,
            "sg3": e_90
        },
        rosettes={
            "R1": {
                "columns": ["sg1", "sg2", "sg3"],
                "type": "rectangular",
                "orientation": 0.0
            }
        },
        coordinates={
            "sg1": {"x": 10.0, "y": 20.0, "z": 0.0}
        }
    )
    
    print(" StrainCollection created.")
    
    # 2. Test Rosette Calculation
    print(" Calculation rosette strains...")
    res = calculate_rosette_strains(col, "R1")
    
    # Expected results:
    # Ep1 = 1000
    # Ep2 = -300
    # Angle = 0
    
    ep1 = res["R1_epsilon1"].values[0]
    ep2 = res["R1_epsilon2"].values[0]
    angle = res["R1_angle"].values[0]
    
    print(f" Result: Ep1={ep1:.2f}, Ep2={ep2:.2f}, Angle={angle:.2f}")
    
    if abs(ep1 - 1000.0) > 1e-5:
        print(f"FAIL: Ep1 expected 1000, got {ep1}")
        sys.exit(1)
        
    if abs(ep2 - -300.0) > 1e-5:
        print(f"FAIL: Ep2 expected -300, got {ep2}")
        sys.exit(1)
        
    if abs(angle - 0.0) > 1e-5:
        # Sometimes angle can be -0 or close to 0
        if abs(angle) > 1e-5:
            print(f"FAIL: Angle expected 0, got {angle}")
            sys.exit(1)

    # 3. Test Visualization (Dry run to ensure no errors)
    print(" Testing visualization (dry run)...")
    try:
        # show=False to prevent blocking
        plot_rosette_vectors(res, step_index=0, show=False)
        print(" Visualization executed without error.")
    except Exception as e:
        print(f"FAIL: Visualization raised error: {e}")
        sys.exit(1)

    # 4. Test Shared Operations (from coordinate domain)
    print(" Testing shared operations (calculate_distance)...")
    try:
        # sg1 and sg2 should have distance
        # But we only set coordinate for sg1 in create_strain_collection above!
        # Let's add coordinates for other gauges first
        res.set_column_coordinates("sg2", x=30.0, y=20.0, z=0.0)
        
        # calculate_distance is imported from ops proxy typically
        # Here we import it directly or use ops proxy if we implemented it
        # Actually verify_strain_domain.py imports specific functions. 
        # Let's import calculate_distance from coordinate domain
        from tascpy.operations.coordinate.distance import calculate_distance
        
        dist = calculate_distance(res, "sg1", "sg2")
        print(f" Distance sg1-sg2: {dist}")
        
        if abs(dist - 20.0) > 1e-5:
            print(f"FAIL: Distance expected 20.0, got {dist}")
            sys.exit(1)
            
    except Exception as e:
        print(f"FAIL: Shared operation error: {e}")
        sys.exit(1)
    
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_strain_domain()
