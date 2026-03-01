
import sys
import os
import numpy as np
import pytest
import math

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step
import tascpy.analytics.operations.core.math # Register operations

def create_test_collection():
    c = ColumnCollection(step=[], columns={})
    c.step = Step(values=[0, 1, 2, 3, 4])
    
    # Values: 0, 1, 4, 9, None
    vals = [0.0, 1.0, 4.0, 9.0, None]
    c.add_column("Val", NumberColumn(None, "Val", "unit", values=vals))
    
    # Angles: 0, 30, 45, 60, 90
    angles = [0.0, 30.0, 45.0, 60.0, 90.0]
    c.add_column("Angle", NumberColumn(None, "Angle", "deg", values=angles))
    
    # Negative: 0, -1, -4, -9, None
    neg = [0.0, -1.0, -4.0, -9.0, None]
    c.add_column("Neg", NumberColumn(None, "Neg", "unit", values=neg))

    return c

def test_sin_cos_tan():
    c = create_test_collection()
    
    # Test sin (degrees)
    res = c.ops.sin(column="Angle", degrees=True)
    # sin(0)=0, sin(30)=0.5, sin(90)=1
    expected = [0.0, 0.5, 1/math.sqrt(2), math.sqrt(3)/2, 1.0]
    np.testing.assert_array_almost_equal(res["sin(Angle)"].values, expected)
    
    # Test cos (degrees)
    res = c.ops.cos(column="Angle", degrees=True)
    # cos(0)=1, cos(60)=0.5, cos(90)=0
    expected = [1.0, math.sqrt(3)/2, 1/math.sqrt(2), 0.5, 0.0]
    np.testing.assert_array_almost_equal(res["cos(Angle)"].values, expected)

def test_sqrt():
    c = create_test_collection()
    res = c.ops.sqrt(column="Val")
    # sqrt(0)=0, sqrt(1)=1, sqrt(4)=2, sqrt(9)=3, None->None
    expected = [0.0, 1.0, 2.0, 3.0, None]
    
    
    # Check values handling None manually
    out = res["sqrt(Val)"].values
    assert np.isnan(out[-1])
    np.testing.assert_array_almost_equal(out[:-1], expected[:-1])
    
    # Test negative sqrt -> None/NaN (warning suppressed expected)
    res = c.ops.sqrt(column="Neg")
    out = res["sqrt(Neg)"].values
    # sqrt(0)=0, others None
    assert out[0] == 0.0
    for i in range(1, 5):
        assert np.isnan(out[i])

def test_pow():
    c = create_test_collection()
    res = c.ops.pow(column="Val", exponent=2)
    # 0^2=0, 1^2=1, 4^2=16, 9^2=81
    out = res["Val^2"].values
    expected = [0.0, 1.0, 16.0, 81.0, None]
    np.testing.assert_array_almost_equal(out[:-1], expected[:-1])
    assert np.isnan(out[-1])

def test_abs_round():
    c = create_test_collection()
    
    # Abs: Neg col: 0, -1, -4, -9, None -> 0, 1, 4, 9, None
    res = c.ops.abs_values(column="Neg")
    out = res["abs(Neg)"].values
    expected = [0.0, 1.0, 4.0, 9.0, None]
    np.testing.assert_array_almost_equal(out[:-1], expected[:-1])
    assert np.isnan(out[-1])
    
    # Round
    # Create float col
    vals = [0.123, 1.567, 2.500, 3.999, None]
    c.add_column("Float", NumberColumn(None, "Float", "", values=vals))
    
    res = c.ops.round_values(column="Float", decimals=1)
    out = res["round(Float, 1)"].values
    expected_r = [0.1, 1.6, 2.5, 4.0, None]
    np.testing.assert_array_almost_equal(out[:-1], expected_r[:-1])
    assert np.isnan(out[-1])

def test_log():
    c = create_test_collection()
    
    # Log base e
    # Val: 0, 1, 4, 9. 0->NaN/None
    res = c.ops.log(column="Val") # default base e
    out = res["log(Val)"].values
    assert np.isnan(out[0]) # log(0) undefined
    assert np.isnan(out[-1])
    assert abs(out[1] - 0.0) < 1e-10 # log(1)=0
    assert abs(out[2] - math.log(4)) < 1e-10
    
    # Log base 10
    res = c.ops.log(column="Val", base=10)
    out = res["log10(Val)"].values
    assert abs(out[1] - 0.0) < 1e-10 # log10(1)=0

def test_normalize():
    c = create_test_collection()
    
    # MinMax: 0, 1, 4, 9 (ignore None). Min=0, Max=9.
    # 0->0, 1->1/9, 4->4/9, 9->1
    res = c.ops.normalize(column="Val", method="minmax")
    out = res["norm_minmax(Val)"].values
    expected = [0.0, 1.0/9.0, 4.0/9.0, 1.0]
    np.testing.assert_array_almost_equal(out[:-1], expected)
    assert np.isnan(out[-1])

    # ZScore
    # vals = [0, 1, 4, 9]. Mean = 3.5. Var = ((3.5^2 + 2.5^2 + 0.5^2 + 5.5^2) / 4)
    # 3.5^2=12.25, 2.5^2=6.25, 0.5^2=0.25, 5.5^2=30.25. Sum=49. Var=12.25. Std=3.5.
    # 0 -> (0-3.5)/3.5 = -1.0
    # 1 -> (1-3.5)/3.5 = -2.5/3.5 = -0.714
    # 4 -> (4-3.5)/3.5 = 0.5/3.5 = 0.142
    # 9 -> (9-3.5)/3.5 = 5.5/3.5 = 1.571
    res = c.ops.normalize(column="Val", method="zscore")
    out = res["norm_zscore(Val)"].values
    expected_z = [-1.0, -0.7142857, 0.1428571, 1.5714286]
    np.testing.assert_array_almost_equal(out[:-1], expected_z, decimal=6)
    assert np.isnan(out[-1])

if __name__ == "__main__":
    test_sin_cos_tan()
    test_sqrt()
    test_log()
    test_log()
    test_pow()
    test_abs_round()
    test_normalize()
    print("All tests passed!")
