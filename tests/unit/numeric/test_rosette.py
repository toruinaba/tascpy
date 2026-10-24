import pytest
import numpy as np
from tascpy.numeric.rosette import compute_rosette_strains

def test_compute_rosette_strains_rectangular():
    e1 = np.array([100.0, 200.0])
    e2 = np.array([50.0, 100.0])
    e3 = np.array([0.0, 0.0])

    emax, emin, gmax, theta = compute_rosette_strains(e1, e2, e3, rosette_type="rectangular")
    assert len(emax) == 2
    assert len(emin) == 2
    assert len(gmax) == 2
    assert len(theta) == 2

def test_compute_rosette_strains_delta():
    e1 = np.array([100.0])
    e2 = np.array([50.0])
    e3 = np.array([0.0])

    emax, emin, gmax, theta = compute_rosette_strains(e1, e2, e3, rosette_type="delta")
    assert len(emax) == 1

def test_compute_rosette_strains_invalid():
    with pytest.raises(ValueError):
        compute_rosette_strains(np.array([1]), np.array([1]), np.array([1]), rosette_type="invalid")
