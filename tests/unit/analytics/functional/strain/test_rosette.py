import pytest
import numpy as np
from tascpy.analytics.functional.strain.rosette import compute_rosette_strains, compute_rosette_vectors

def test_compute_rosette_strains_rectangular():
    e1 = np.array([100.0, 200.0])
    e2 = np.array([50.0, 100.0])
    e3 = np.array([0.0, 0.0])

    emax, emin, gmax, theta = compute_rosette_strains(e1, e2, e3, r_type="rectangular")
    assert len(emax) == 2
    assert len(emin) == 2
    assert len(gmax) == 2
    assert len(theta) == 2

def test_compute_rosette_strains_delta():
    e1 = np.array([100.0])
    e2 = np.array([50.0])
    e3 = np.array([0.0])

    emax, emin, gmax, theta = compute_rosette_strains(e1, e2, e3, r_type="delta")
    assert len(emax) == 1

def test_compute_rosette_strains_invalid():
    with pytest.raises(ValueError):
        compute_rosette_strains(np.array([1]), np.array([1]), np.array([1]), r_type="invalid")

def test_compute_rosette_vectors():
    v1x, v1y, v2x, v2y = compute_rosette_vectors(100.0, 50.0, 45.0, scale=1.0)
    assert isinstance(v1x, np.float64) or isinstance(v1x, float)
    assert isinstance(v1y, np.float64) or isinstance(v1y, float)
    assert isinstance(v2x, np.float64) or isinstance(v2x, float)
    assert isinstance(v2y, np.float64) or isinstance(v2y, float)
