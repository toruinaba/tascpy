import unittest
import numpy as np
from tascpy.domains.strain import StrainCollection, create_strain_collection
from tascpy.core.column import Column
from tascpy.operations.strain.rosette import calculate_rosette_strains

class TestStrainDomain(unittest.TestCase):
    def setUp(self):
        # Synthetic data for pure uniaxial tension along X-axis
        # ex = 1000, ey = -300 (Poisson 0.3), gamma = 0
        # Rectangular rosette at 0, 45, 90
        # e1 (0) = ex = 1000
        # e3 (90) = ey = -300
        # e2 (45) = (ex + ey + gamma)/2 = (1000 - 300)/2 = 350
        
        self.e1_val = 1000.0
        self.e2_val = 350.0
        self.e3_val = -300.0
        
        self.n_steps = 10
        
        self.collection = create_strain_collection(
            step=list(range(self.n_steps)),
            columns={
                "ch1": Column(ch="ch1", name="ch1", unit="uE", values=[self.e1_val]*self.n_steps),
                "ch2": Column(ch="ch2", name="ch2", unit="uE", values=[self.e2_val]*self.n_steps),
                "ch3": Column(ch="ch3", name="ch3", unit="uE", values=[self.e3_val]*self.n_steps)
            },
            coordinates={
                "ch1": {"x": 10, "y": 20, "z": 0},
                "ch2": {"x": 10, "y": 20, "z": 0},
                "ch3": {"x": 10, "y": 20, "z": 0}
            },
            rosettes={
                "R1": {
                    "columns": ["ch1", "ch2", "ch3"],
                    "type": "rectangular",
                    "orientation": 0.0
                }
            }
        )

    def test_rosette_metadata(self):
        rosette = self.collection.get_rosette("R1")
        self.assertIsNotNone(rosette)
        self.assertEqual(rosette["type"], "rectangular")
        self.assertEqual(rosette["columns"], ["ch1", "ch2", "ch3"])

    def test_calculation(self):
        result = calculate_rosette_strains(self.collection, rosette_name="R1")
        
        # Check newly created columns
        self.assertIn("R1_e1", result.columns) # Max principal
        self.assertIn("R1_e2", result.columns) # Min principal
        self.assertIn("R1_gamma", result.columns)
        self.assertIn("R1_theta", result.columns)
        
        # Verify values
        # e_max should be 1000 (ex)
        # e_min should be -300 (ey)
        # theta should be 0
        
        e_max = result["R1_e1"].values[0]
        e_min = result["R1_e2"].values[0]
        theta = result["R1_theta"].values[0]
        
        self.assertAlmostEqual(e_max, 1000.0)
        self.assertAlmostEqual(e_min, -300.0)
        self.assertAlmostEqual(theta, 0.0)
        
        # Verify coordinates are propagated
        x, y, z = result.get_column_coordinates("R1_e1")
        self.assertEqual(x, 10)
        self.assertEqual(y, 20)
        
    def test_delta_calculation(self):
        # Test Delta rosette logic (0, 60, 120)
        # Uniaxial stress state: ex=1000, ey=-300, gamma=0
        # e(theta) = (ex+ey)/2 + (ex-ey)/2*cos(2theta) + gamma/2*sin(2theta)
        
        ex = 1000
        ey = -300
        
        def e_at(deg):
            rad = np.radians(deg)
            return (ex+ey)/2 + (ex-ey)/2 * np.cos(2*rad)
            
        e_0 = e_at(0)    # 1000
        e_60 = e_at(60)  # 350 - 650*0.5 = 25
        e_120 = e_at(120) # 350 - 650*0.5 = 25
        
        col = create_strain_collection(
            step=[0],
            columns={
                "c1": Column(ch=None, name="c1", unit="uE", values=[e_0]),
                "c2": Column(ch=None, name="c2", unit="uE", values=[e_60]),
                "c3": Column(ch=None, name="c3", unit="uE", values=[e_120])
            },
            rosettes={
                "D1": {
                    "columns": ["c1", "c2", "c3"],
                    "type": "delta",
                    "orientation": 0.0
                }
            }
        )
        
        res = calculate_rosette_strains(col, rosette_name="D1")
        self.assertAlmostEqual(res["D1_e1"].values[0], 1000.0)
        self.assertAlmostEqual(res["D1_e2"].values[0], -300.0)

if __name__ == "__main__":
    unittest.main()
