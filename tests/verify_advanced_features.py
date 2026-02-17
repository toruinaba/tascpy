
import unittest
import numpy as np
import pandas as pd
from tascpy.core.collection import ColumnCollection, Column
from tascpy.core.step import Step
from tascpy.operations.core.combine import switch_by_step
from tascpy.operations.core.filters import remove_outliers

class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        # Setup data
        self.steps = np.arange(10)
        self.v1 = np.zeros(10)
        self.v2 = np.ones(10)
        # For switch_by_step: threshold at 5
        
        self.collection = ColumnCollection(Step(self.steps, "time"), {})
        self.collection.add_column("v1", Column("ch1", "v1", "unit", self.v1))
        self.collection.add_column("v2", Column("ch2", "v2", "unit", self.v2))
        
        # For remove_outliers
        # Simpler case: constant values with small spike
        # [1, 1, 1, 2, 1, 1]
        self.outlier_vals = np.array([1.0, 1.0, 1.0, 2.0, 1.0, 1.0])
        self.outlier_steps = np.arange(6)
        self.outlier_coll = ColumnCollection(Step(self.outlier_steps, "time"), {})
        self.outlier_coll.add_column("vals", Column("ch", "vals", "unit", self.outlier_vals))

    def test_switch_by_step_metadata(self):
        """Verify metadata injection in switch_by_step"""
        threshold = 4.5
        res = switch_by_step(
            self.collection, "v1", "v2", 
            threshold=threshold, 
            compare_mode="value",
            result_column="switched"
        )
        
        # Check result
        # Steps < 4.5 -> v1 (0), Steps >= 4.5 -> v2 (1)
        expected = np.where(self.steps < threshold, 0.0, 1.0)
        np.testing.assert_array_equal(res["switched"].values, expected)
        
        # Check metadata
        meta = res.metadata
        print("Metadata:", meta)
        self.assertIn("operation", meta)
        self.assertEqual(meta["operation"], "switch_by_step")
        self.assertEqual(meta["threshold"], threshold)
        self.assertEqual(meta["compare_mode"], "value")

    def test_remove_outliers_pipeline(self):
        """Verify remove_outliers pipeline"""
        res = remove_outliers(
            self.outlier_coll, "vals", 
            window_size=3, 
            threshold=0.5
        )
        
        print("Original length:", len(self.outlier_coll))
        print("Filtered length:", len(res))
        
        # Should remove index 3 (10.0)
        self.assertEqual(len(res), 5)
        self.assertTrue(10.0 not in res["vals"].values)
        
        # Verify step filtering
        self.assertTrue(3 not in res.step.values)

if __name__ == "__main__":
    unittest.main()
