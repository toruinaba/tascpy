
import sys
import os
import math
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step

def create_test_collection():
    c = ColumnCollection(step=[], columns={})
    c.step = Step(values=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    
    # Normal data with one outlier
    # Mean ~1.0, One huge value 100.0
    vals = [1.0, 1.1, 0.9, 1.0, 100.0, 1.0, 0.9, 1.1, 1.0, 1.0]
    c.add_column("Data", NumberColumn(None, "Data", None, values=vals))
    
    # Data with None
    vals_none = [1.0, None, 3.0, None, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    c.add_column("WithNone", NumberColumn(None, "WithNone", None, values=vals_none))

    return c

def test_outliers():
    c = create_test_collection()
    
    # Detect outliers
    # Window=3. 
    # At index 4 (100.0). Neighbors 1.0, 1.0. MA ~34. 
    # Diff |100 - 34| = 66. Ratio 66/34 > 0.5. Should be outlier.
    res = c.ops.detect_outliers("Data", window_size=3, threshold=0.5)
    
    outlier_col = "outlier(Data)"
    assert outlier_col in res.columns
    flags = res[outlier_col].values
    assert flags[4] == 1
    assert flags[0] == 0
    print("Pass: detect_outliers")

def test_gaussian():
    c = create_test_collection()
    
    # Gaussian filter should smooth the outlier (reduce peak)
    res = c.ops.gaussian_filter("Data", sigma=1.0)
    
    smoothed_col = "gaussian(col=Data,sigma=1.0)"
    assert smoothed_col in res.columns
    val = res[smoothed_col].values[4]
    
    # Original 100. Smoothed should be significantly less.
    assert val < 90.0
    print("Pass: gaussian_filter")

def test_aggregations():
    c = create_test_collection()
    
    # Max of Data is 100.0
    max_val = c.ops.max("Data")
    assert max_val == 100.0
    
    # WithNone col: [1, None, 3, None, 5...] max 10.
    # Should ignore None
    max_none = c.ops.max("WithNone")
    assert max_none == 10.0
    
    # Mean
    mean_val = c.ops.mean("WithNone")
    # 1+3+5+6+7+8+9+10 = 49. Count=8. Mean=6.125
    assert abs(mean_val - 6.125) < 1e-9
    
    print("Pass: aggregations")

if __name__ == "__main__":
    test_outliers()
    test_gaussian()
    test_aggregations()
