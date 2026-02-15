
import unittest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.core.column import Column
from tascpy.operations.load_displacement.cycles import (
    find_peaks_and_valleys,
    analyze_hysteresis,
    analyze_stiffness_degradation,
    cycle_count
)

class TestCyclicAnalysis(unittest.TestCase):
    def setUp(self):
        # Create synthetic cyclic data
        t = np.linspace(0, 4 * np.pi, 200) # 2 cycles
        # Displacement: sine wave
        disp = 10 * np.sin(t)
        # Load: sine wave with phase lag (hysteresis) + noise
        load = 100 * np.sin(t + 0.5) 
        
        self.step = t.tolist()
        self.disp = disp.tolist()
        self.load = load.tolist()
        
        self.collection = LoadDisplacementCollection(
            step=self.step,
            columns={
                "Load": Column(ch=None, name="Load", unit="kN", values=self.load),
                "Displacement": Column(ch=None, name="Displacement", unit="mm", values=self.disp)
            },
            load_column="Load",
            displacement_column="Displacement"
        )

    def test_peak_detection(self):
        # Find peaks in Displacement
        peaks = find_peaks_and_valleys(
            self.collection, 
            column="Displacement", 
            distance=10
        )
        flags = peaks["peak_valley"].values
        
        # Should have approx 2 peaks and 2 valleys
        n_peaks = sum(1 for f in flags if f == 1)
        n_valleys = sum(1 for f in flags if f == -1)
        
        self.assertGreaterEqual(n_peaks, 2)
        self.assertGreaterEqual(n_valleys, 2)

    def test_hysteresis_area(self):
        # Create a single perfect ellipse loop
        theta = np.linspace(0, 2*np.pi, 100)
        a = 2.0 # disp amplitude
        b = 10.0 # load amplitude
        # Parametric equation of ellipse: x = a*cos(theta), y = b*sin(theta)
        # Area = pi * a * b
        
        disp = a * np.cos(theta)
        load = b * np.sin(theta)
        
        coll = LoadDisplacementCollection(
            step=list(range(100)),
            columns={
                "Load": Column(ch=None, name="Load", unit="kN", values=load.tolist()),
                "Displacement": Column(ch=None, name="Displacement", unit="mm", values=disp.tolist()),
                "Cycle": Column(ch=None, name="Cycle", unit=None, values=[1]*100) # Single cycle
            },
            load_column="Load",
            displacement_column="Displacement"
        )
        
        result = analyze_hysteresis(coll, cycle_column="Cycle")
        area = result["energy"].values[0]
        expected_area = np.pi * a * b
        
        print(f"Calculated Area: {area}, Expected: {expected_area}")
        # Allow small error due to discrete points
        self.assertAlmostEqual(area, expected_area, delta=expected_area * 0.05)

    def test_stiffness_degradation(self):
        # Create data with decreasing stiffness
        # Cycle 1: k=10, Cycle 2: k=5
        t1 = np.linspace(0, 2*np.pi, 50)
        d1 = np.sin(t1)
        l1 = 10 * d1
        
        t2 = np.linspace(2*np.pi, 4*np.pi, 50)
        d2 = np.sin(t2)
        l2 = 5 * d2
        
        disp = np.concatenate([d1, d2])
        load = np.concatenate([l1, l2])
        cycles = [1]*50 + [2]*50
        
        coll = LoadDisplacementCollection(
            step=list(range(100)),
            columns={
                "Load": Column(ch=None, name="Load", unit="kN", values=load.tolist()),
                "Displacement": Column(ch=None, name="Displacement", unit="mm", values=disp.tolist()),
                "Cycle": Column(ch=None, name="Cycle", unit=None, values=cycles)
            },
            load_column="Load",
            displacement_column="Displacement"
        )
        
        result = analyze_stiffness_degradation(coll, cycle_column="Cycle")
        k = result["stiffness"].values
        
        print(f"Stiffnesses: {k}")
        self.assertAlmostEqual(k[0], 10.0, places=1)
        self.assertAlmostEqual(k[1], 5.0, places=1)

if __name__ == "__main__":
    unittest.main()
