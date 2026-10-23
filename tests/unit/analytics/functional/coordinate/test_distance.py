import numpy as np
import pytest

from tascpy.analytics.functional.coordinate.distance import euclidean_distance


def test_euclidean_distance():
    assert np.isclose(euclidean_distance([0.0, 0.0], [3.0, 4.0]), 5.0)
    assert np.isclose(euclidean_distance([0.0, 0.0, 0.0], [1.0, 2.0, 2.0]), 3.0)
    assert euclidean_distance([1.0, 2.0], [1.0, 2.0]) == 0.0


def test_euclidean_distance_dimension_mismatch():
    with pytest.raises(ValueError, match="次元"):
        euclidean_distance([0.0, 0.0], [0.0, 0.0, 1.0])
