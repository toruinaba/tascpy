import pytest
import numpy as np
from tascpy.core.column import Column
from tascpy.domains.strain import create_strain_collection
from tascpy.analytics.operations.strain.abstraction import (
    resolve_rosette_strains,
    resolve_stress_strain,
    resolve_stress_calculation
)

# Dummy pure functions to decorate
def dummy_rosette(e1, e2, e3, r_type, angle_offset):
    return e1 + 1, e2 + 1, e3 + 1, e1 + 10

def dummy_stress_strain(stress, strain, lateral_strain, elastic_range, offset):
    return 200000.0, 0.002, 400.0, 0.3 if lateral_strain is not None else np.nan

def dummy_stress_calc(load_vals, area):
    return load_vals / area

@pytest.fixture
def strain_coll():
    sc = create_strain_collection(
        step=[1],
        columns={
            "e1": Column("1", "e1", "ue", [100.0]),
            "e2": Column("2", "e2", "ue", [50.0]),
            "e3": Column("3", "e3", "ue", [0.0]),
            "load": Column("4", "load", "N", [1000.0]),
            "stress": Column("stress", "stress", "MPa", [200.0]),
            "strain": Column("strain", "strain", "", [0.001]),
            "lat": Column("lat", "lat", "", [-0.0003])
        },
        rosettes={"R1": {"columns": ["e1", "e2", "e3"], "type": "rectangular", "orientation": 0.0}}
    )
    sc.set_column_coordinates("e1", 0, 0, 0)
    return sc

def test_resolve_rosette_strains(strain_coll):
    @resolve_rosette_strains()
    def compute(e1, e2, e3, r_type, angle_offset):
        return dummy_rosette(e1, e2, e3, r_type, angle_offset)
    
    # Via rosette name
    res1 = compute(strain_coll, rosette_name="R1")
    assert "R1_e1" in res1.columns

    # Via explicit columns
    res2 = compute(strain_coll, columns=["e1", "e2", "e3"], prefix="my_prefix")
    assert "my_prefix_e1" in res2.columns

    # Check error handling
    with pytest.raises(ValueError):
        compute(strain_coll, columns=["e1"])  # not 3 columns

    with pytest.raises(ValueError):
        compute(strain_coll, columns=["e1", "e2", "missing"])

def test_resolve_stress_strain(strain_coll):
    @resolve_stress_strain()
    def compute(stress, strain, lateral_strain, elastic_range, offset):
        return dummy_stress_strain(stress, strain, lateral_strain, elastic_range, offset)
    
    # Missing kwargs but present in args fallback is NOT fullly supported dynamically without args, 
    # but the abstraction natively supports args fallback
    E, ys_strain, ys_stress, nu = compute(strain_coll, "stress", "strain")
    assert E == 200000.0
    assert np.isnan(nu)

    # With lateral strain
    E, ys_strain, ys_stress, nu = compute(strain_coll, "stress", "strain", lateral_strain_column="lat")
    assert nu == 0.3

    with pytest.raises(ValueError):
         compute(strain_coll, stress_column="missing", strain_column="strain")

def test_resolve_stress_calculation(strain_coll):
    @resolve_stress_calculation()
    def compute(load_vals, area):
        return dummy_stress_calc(load_vals, area)
    
    res = compute(strain_coll, "load", 10.0, result_column="my_stress")
    assert "my_stress" in res.columns
    assert res["my_stress"].values[0] == 100.0

    with pytest.raises(ValueError):
        compute(strain_coll, "missing", 10.0)
