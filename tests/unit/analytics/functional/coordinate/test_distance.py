import pytest
import numpy as np
from tascpy.analytics.functional.coordinate.distance import compute_euclidean_distance

def test_compute_euclidean_distance():
    # 2D case
    dist_2d = compute_euclidean_distance(0.0, 0.0, 3.0, 4.0)
    assert np.isclose(dist_2d, 5.0)
    
    # 3D case
    dist_3d = compute_euclidean_distance(0.0, 0.0, 1.0, 2.0, 0.0, 2.0)
    assert np.isclose(dist_3d, 3.0) # sqrt(1+4+4) = 3
    
    # Mixed None in z
    dist_mixed1 = compute_euclidean_distance(0.0, 0.0, 3.0, 4.0, p1_z=1.0) # p2_z is None -> 0.0
    assert np.isclose(dist_mixed1, np.sqrt(9 + 16 + 1))
    
    dist_mixed2 = compute_euclidean_distance(0.0, 0.0, 3.0, 4.0, p2_z=2.0) # p1_z is None -> 0.0
    assert np.isclose(dist_mixed2, np.sqrt(9 + 16 + 4))

    # Same points
    dist_zero = compute_euclidean_distance(1.0, 2.0, 1.0, 2.0)
    assert np.isclose(dist_zero, 0.0)
