
import sys
import os
import numpy as np
import pytest

# Apply path trick
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step
from tascpy.operations.core.stats import moving_average, detect_outliers, gaussian_filter, max as c_max, min as c_min, mean as c_mean, std as c_std

def create_test_collection():
    steps = [0.1 * i for i in range(10)]
    # A: Linear
    col_a_vals = [i for i in range(10)] 
    # B: Outlier at index 5
    col_b_vals = [10.0] * 10
    col_b_vals[5] = 100.0
    # C: None values
    col_c_vals = [1.0, 2.0, None, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    
    coll = ColumnCollection(step=Step(values=steps), columns={})
    coll.add_column("A", NumberColumn("CH1", "A", "N", col_a_vals))
    coll.add_column("B", NumberColumn("CH2", "B", "mm", col_b_vals))
    coll.add_column("C", NumberColumn("CH3", "C", "N", col_c_vals))
    return coll

def test_moving_average():
    c = create_test_collection()
    # Simple MA window=3. 
    # A: 0,1,2,3... -> MA at 1: (0+1+2)/3=1. MA at 2: (1+2+3)/3=2.
    res = moving_average(c, "A", window_size=3)
    
    # Check result column exists
    res_col_name = "ma3(A)"
    assert res_col_name in res.columns
    
    vals = res[res_col_name].values
    assert vals[1] == 1.0
    assert vals[2] == 2.0
    
    print("Pass: moving_average")

def test_detect_outliers():
    c = create_test_collection()
    # B has outlier 100 at index 5. Normal is 10.
    res = detect_outliers(c, "B", window_size=3, threshold=0.5)
    
    res_col_name = "outlier(B)"
    assert res_col_name in res.columns
    
    flags = res[res_col_name].values
    assert flags[5] == 1
    assert flags[0] == 0
    
    print("Pass: detect_outliers")

def test_gaussian_filter():
    c = create_test_collection()
    # A is linear, so gaussian should be close to linear except edges
    res = gaussian_filter(c, "A", sigma=1.0)
    
    res_col_name = "gaussian(col=A,sigma=1.0)"
    assert res_col_name in res.columns
    
    # Just check it runs and produces floats
    vals = res[res_col_name].values
    assert isinstance(vals[5], float)
    
    print("Pass: gaussian_filter")

def test_aggregations():
    c = create_test_collection()
    
    # A: 0..9
    assert c_max(c, "A") == 9.0
    assert c_min(c, "A") == 0.0
    assert c_mean(c, "A") == 4.5
    
    # C: 1, 2, None, 4, ...
    # Ignoring None: 1,2,4,5,6,7,8,9,10. Sum=52. Count=9. Mean=5.77...
    # Wait, 1+2=3. 4+5+6+7+8+9+10 = 49. Total 52.
    assert np.isclose(c_mean(c, "C"), 52/9)
    
    print("Pass: aggregations")

if __name__ == "__main__":
    test_moving_average()
    test_detect_outliers()
    test_gaussian_filter()
    test_aggregations()
