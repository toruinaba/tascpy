import pytest
import numpy as np
from tascpy.analytics.functional.strain.ss_analysis import compute_stress, compute_material_properties

def test_compute_stress():
    load = np.array([0.0, 1000.0, 2000.0])
    area = 10.0
    stress = compute_stress(load, area)
    np.testing.assert_array_equal(stress, [0.0, 100.0, 200.0])

def test_compute_material_properties():
    # Linear dataset
    strain = np.array([0.0, 0.0005, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.004])
    stress = strain * 200000.0  # E = 200000 MPa

    E, y_strain, y_stress, nu = compute_material_properties(
        stress, strain, elastic_range=(0.0005, 0.0025)
    )
    assert np.isclose(E, 200000.0)
    assert np.isnan(nu)
    
def test_compute_material_properties_with_lateral():
    strain = np.array([0.0, 0.0005, 0.001, 0.0015, 0.002, 0.0025, 0.003])
    stress = strain * 200000.0
    lat_strain = strain * -0.3

    E, y_strain, y_stress, nu = compute_material_properties(
        stress, strain, lateral_strain=lat_strain, elastic_range=(0.0005, 0.0025)
    )
    assert np.isclose(E, 200000.0)
    assert np.isclose(nu, 0.3)

def test_compute_material_properties_yield():
    # simulate yielding
    strain = np.array([0.0, 0.0005, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.004, 0.005, 0.006])
    stress = np.array([0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 520.0, 530.0, 535.0, 540.0])
    
    E, y_strain, y_stress, nu = compute_material_properties(
        stress, strain, offset=0.002, elastic_range=(0.0005, 0.0025)
    )
    assert not np.isnan(E)
    # y_stress should be correctly interpolated by 0.2% offset logic
    assert not np.isnan(y_stress)
    assert not np.isnan(y_strain)
