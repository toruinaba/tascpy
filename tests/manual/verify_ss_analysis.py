import unittest
import numpy as np
from tascpy.domains.strain import create_strain_collection
from tascpy.core.column import Column
from tascpy.analytics.operations.strain.ss_analysis import calculate_stress, analyze_material_properties

class TestSSAnalysis(unittest.TestCase):
    def setUp(self):
        # Create synthetic Stress-Strain data/
        # Material: Steel-ish
        # E = 200 GPa = 200000 MPa
        # Yield = 300 MPa
        # Nu = 0.3
        
        self.E_true = 200000.0
        self.Yield_true = 300.0
        self.Nu_true = 0.3
        self.Area = 100.0 # mm2
        
        # Strain: 0 to 0.01
        self.strain = np.linspace(0, 0.01, 100)
        
        # Stress: Bilinear
        # Elastic region (epsilon < 300/200000 = 0.0015)
        yield_strain = self.Yield_true / self.E_true
        
        self.stress = np.zeros_like(self.strain)
        elastic_mask = self.strain <= yield_strain
        plastic_mask = ~elastic_mask
        
        self.stress[elastic_mask] = self.E_true * self.strain[elastic_mask]
        # Plastic: slight hardening (slope E/100)
        self.stress[plastic_mask] = self.Yield_true + (self.E_true/100) * (self.strain[plastic_mask] - yield_strain)
        
        # Load = Stress * Area
        self.load = self.stress * self.Area
        
        # Lateral Strain = -nu * strain (elastic)
        # Plastic nu is 0.5, but let's keep it simple for now (0.3 everywhere effectively or just check elastic)
        self.lat_strain = -self.Nu_true * self.strain
        
        self.collection = create_strain_collection(
            step=list(range(100)),
            columns={
                "Load": Column(ch="Load", name="Load", unit="N", values=self.load.tolist()),
                "Strain": Column(ch="Strain", name="Strain", unit="", values=self.strain.tolist()),
                "LatStrain": Column(ch="LatStrain", name="LatStrain", unit="", values=self.lat_strain.tolist())
            }
        )
        
    def test_stress_calc(self):
        # Calculate Stress
        res = calculate_stress(self.collection, load_column="Load", area=self.Area, result_column="Stress", unit="MPa")
        
        self.assertIn("Stress", res.columns)
        stress_vals = res["Stress"].values
        
        # Check max stress
        expected_max = np.max(self.stress)
        calc_max = np.max(stress_vals)
        self.assertAlmostEqual(calc_max, expected_max)
        
    def test_material_properties(self):
        # First calculate stress
        res = calculate_stress(self.collection, load_column="Load", area=self.Area, result_column="Stress", unit="MPa")
        
        # Analyze
        # Elastic range: 0.0000 to 0.0010 (Yield is at 0.0015)
        props = analyze_material_properties(
            res, 
            stress_column="Stress", 
            strain_column="Strain", 
            lateral_strain_column="LatStrain",
            elastic_range=(0.0, 0.001),
            offset=0.002
        )
        
        # 1. Young's Modulus
        e_res = props.get_result("material_E")
        self.assertAlmostEqual(e_res.value, self.E_true, delta=self.E_true*0.01)
        
        # 2. Poisson's Ratio
        nu_res = props.get_result("material_nu")
        self.assertAlmostEqual(nu_res.value, self.Nu_true, delta=0.01)
        
        # 3. Yield Strength (0.2% offset)
        # Offset line starts at 0.002.
        # Intersects the simple hardening curve.
        # Intersection calc:
        # Eq1 (material): sigma = Yield + Et(epsilon - epsilon_y)  (for epsilon > epsilon_y)
        # Eq2 (offset):   sigma = E(epsilon - 0.002)
        # Solve for sigma.
        # This is strictly math, but let's just check if it found *something* reasonable.
        # Since hardenning is very low (E/100), yield strength should be close to Yield_true + a bit.
        
        y_res = props.get_result("material_yield")
        self.assertIsNotNone(y_res)
        # Since it's 0.2% offset, and yield strain is 0.15%, the intersection is definitely in plastic region.
        # It should be > Yield_true
        self.assertGreater(y_res.y, self.Yield_true)
        # Should be less than Ultimate stress
        self.assertLess(y_res.y, np.max(self.stress))

if __name__ == "__main__":
    unittest.main()
