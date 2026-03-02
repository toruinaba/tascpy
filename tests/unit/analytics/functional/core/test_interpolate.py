import pytest
import numpy as np
from tascpy.analytics.functional.interpolate import interpolate_core, calculate_new_axis, partition_data

def test_interpolate_core_numeric():
    base_values = np.array([1.0, 3.0, 5.0])
    numeric_data = {
        "temp": np.array([20.0, 40.0, 60.0]),
        "pressure": np.array([1.0, 2.0, 3.0])
    }
    other_data = {}
    new_axis = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    res = interpolate_core(base_values, numeric_data, other_data, new_axis)
    
    np.testing.assert_allclose(res["temp"], [20.0, 30.0, 40.0, 50.0, 60.0])
    np.testing.assert_allclose(res["pressure"], [1.0, 1.5, 2.0, 2.5, 3.0])

def test_interpolate_core_other():
    base_values = np.array([1.0, 3.0, 5.0])
    numeric_data = {}
    other_data = {
        "status": np.array(["low", "medium", "high"])
    }
    new_axis = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    res = interpolate_core(base_values, numeric_data, other_data, new_axis)
    # Expected nearest neighbor behavior for other data
    np.testing.assert_array_equal(res["status"], ["low", "medium", "medium", "high", "high"])

def test_interpolate_core_extrapolation():
    base_values = np.array([1.0, 3.0, 5.0])
    numeric_data = {
        "temp": np.array([20.0, 40.0, 60.0])
    }
    other_data = {}
    new_axis = np.array([0.0, 6.0])
    
    res = interpolate_core(base_values, numeric_data, other_data, new_axis)
    np.testing.assert_allclose(res["temp"], [10.0, 70.0])

def test_calculate_new_axis():
    base_values = np.array([1.0, 5.0])
    
    res_x = calculate_new_axis(base_values, x_values=[2, 3])
    np.testing.assert_array_equal(res_x, [2, 3])
    
    res_p = calculate_new_axis(base_values, point_count=5)
    np.testing.assert_allclose(res_p, [1.0, 2.0, 3.0, 4.0, 5.0])
    
    with pytest.raises(ValueError):
        calculate_new_axis(base_values)
        
    with pytest.raises(ValueError):
        calculate_new_axis(base_values, x_values=[1], point_count=2)

def test_partition_data_auto():
    data = {
        "a": np.array([1.0, 2.0]),
        "b": np.array(["x", "y"]),
        "c": np.array([1, 2])
    }
    num, other = partition_data(data)
    
    assert "a" in num
    assert "c" in num
    assert "b" in other

def test_partition_data_manual():
    data = {
        "a": np.array([1.0, 2.0]),
        "b": np.array([10.0, 20.0])
    }
    num, other = partition_data(data, numeric_keys=["a"])
    
    assert "a" in num
    assert "b" in other
