import pytest
import numpy as np
from tascpy.analytics.functional.coordinate.basic import extract_coordinates

def test_extract_coordinates():
    # Test arrays
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    z = np.array([7, 8, 9])
    
    res = extract_coordinates(x, y, z)
    np.testing.assert_array_equal(res["x"], x)
    np.testing.assert_array_equal(res["y"], y)
    np.testing.assert_array_equal(res["z"], z)

    # Test scalars
    res = extract_coordinates(1.0, 2.0, 3.0, length=3)
    np.testing.assert_array_equal(res["x"], [1.0, 1.0, 1.0])
    np.testing.assert_array_equal(res["y"], [2.0, 2.0, 2.0])
    np.testing.assert_array_equal(res["z"], [3.0, 3.0, 3.0])

    # Test partial
    res = extract_coordinates(x_array=None, y_array=2.0, length=2)
    assert "x" not in res
    np.testing.assert_array_equal(res["y"], [2.0, 2.0])
