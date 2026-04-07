import pytest
import numpy as np
from tascpy.analytics.functional.coordinate.interpolation import (
    inverse_distance_weighting,
    nearest_neighbor,
    linear_interpolation,
    compute_point_interpolation_values,
    compute_grid_interpolation_values,
    compute_spatial_interpolation_values
)

@pytest.fixture
def point_data():
    return {
        "point": {"x": 1.0, "y": 1.0, "z": 1.0},
        "value": 10.0,
        "col_name": "val"
    }

@pytest.fixture
def multiple_source_data():
    return [
        {"point": {"x": 0.0, "y": 0.0, "z": 0.0}, "value": 10.0},
        {"point": {"x": 2.0, "y": 0.0, "z": 0.0}, "value": 20.0},
        {"point": {"x": 0.0, "y": 2.0, "z": 0.0}, "value": 30.0},
    ]

def test_inverse_distance_weighting(point_data):
    # Same point
    res1 = inverse_distance_weighting(point_data, 1.0, 1.0, 1.0, power=2.0)
    assert np.isclose(res1, 10.0)
    
    # Different point 3D
    res2 = inverse_distance_weighting(point_data, 1.0, 1.0, 2.0, power=2.0)
    # dist = 1.0, weight = 1.0
    assert np.isclose(res2, 10.0)
    
    # Different point 2D (z=None)
    res3 = inverse_distance_weighting(point_data, 1.0, 3.0, None, power=2.0)
    # dist = 2.0, weight = 1 / 4
    assert np.isclose(res3, 10.0 * 0.25)

def test_nearest_neighbor(point_data):
    res = nearest_neighbor(point_data, 100.0, 100.0, 100.0, power=1.0)
    assert np.isclose(res, 10.0)

def test_linear_interpolation(point_data):
    # Same as idw with power=1.0
    res = linear_interpolation(point_data, 1.0, 3.0, None, power=99.0) # power ignored, always 1.0
    # dist = 2.0, weight = 1 / 2.0
    assert np.isclose(res, 10.0 * 0.5)

def test_compute_point_interpolation_values(multiple_source_data):
    res_idw = compute_point_interpolation_values(multiple_source_data, 1.0, 0.0, 0.0, "inverse_distance", 2.0)
    assert len(res_idw) == 3
    # pt1: dist=1, w=1, val=10 -> 10
    # pt2: dist=1, w=1, val=20 -> 20
    # pt3: dist=sqrt(1+4)=sqrt(5), w=1/5, val=30 -> 6
    assert np.allclose(res_idw, [10.0, 20.0, 6.0])

    res_nn = compute_point_interpolation_values(multiple_source_data, 1.0, 0.0, 0.0, "nearest", 2.0)
    assert np.allclose(res_nn, [10.0, 20.0, 30.0])

    res_lin = compute_point_interpolation_values(multiple_source_data, 1.0, 0.0, 0.0, "linear", 2.0)
    # dists are 1, 1, sqrt(5). weights: 1, 1, 1/sqrt(5) 
    assert len(res_lin) == 3

    with pytest.raises(ValueError):
        compute_point_interpolation_values(multiple_source_data, 1.0, 0.0, 0.0, "invalid", 2.0)

def test_compute_grid_interpolation_values(point_data):
    x_grid = np.array([0.0, 1.0, 2.0])
    y_grid = np.array([0.0, 1.0, 2.0])
    
    grid_idw = compute_grid_interpolation_values(point_data, x_grid, y_grid, "inverse_distance", 2.0)
    assert grid_idw.shape == (3, 3)
    # The center (1,1) is exactly the point -> should be 10.0
    assert np.isclose(grid_idw[1, 1], 10.0)

    grid_nn = compute_grid_interpolation_values(point_data, x_grid, y_grid, "nearest", 2.0)
    assert np.isclose(grid_nn[0, 0], 10.0)

    grid_lin = compute_grid_interpolation_values(point_data, x_grid, y_grid, "linear", 2.0)
    assert np.isclose(grid_lin[1, 1], 10.0)

def test_compute_spatial_interpolation_values(multiple_source_data):
    target_coords = [
        {"x": 1.0, "y": 0.0},
        {"x": 1.0, "y": 1.0, "z": 1.0}
    ]

    res_idw = compute_spatial_interpolation_values(multiple_source_data, target_coords, is_3d=False, method="inverse_distance", power=2.0)
    assert len(res_idw) == 2
    # target 1: means of [10.0, 20.0, 6.0] = 36 / 3 = 12.0
    assert np.isclose(res_idw[0], 12.0)

    res_nn = compute_spatial_interpolation_values(multiple_source_data, target_coords, is_3d=True, method="nearest", power=2.0)
    assert np.allclose(res_nn, [20.0, 20.0])
    
    res_lin = compute_spatial_interpolation_values(multiple_source_data, target_coords, is_3d=False, method="linear", power=2.0)
    assert len(res_lin) == 2

    # empty source data
    res_empty = compute_spatial_interpolation_values([], target_coords, is_3d=False, method="nearest", power=2.0)
    assert np.isnan(res_empty[0])
