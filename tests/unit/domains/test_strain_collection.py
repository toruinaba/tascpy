import pytest
from tascpy.core.step import Step
from tascpy.core.column import Column
from tascpy.domains.strain import StrainCollection, create_strain_collection

def test_strain_collection_init():
    sc = StrainCollection(
        step=Step([1, 2, 3]),
        columns={"ch1": Column("ch1", "n", "", [1,2,3])},
        rosettes={"R1": {"columns": ["ch1", "ch2", "ch3"], "type": "rectangular", "orientation": 0.0}}
    )

    assert sc.domain == "strain"
    assert sc.rosette_metadata_key == "rosettes"
    assert "strain_domain" in sc.metadata
    assert sc.get_rosette("R1") is not None
    assert sc.get_rosettes() == {"R1": {"columns": ["ch1", "ch2", "ch3"], "type": "rectangular", "orientation": 0.0}}

def test_strain_collection_add_rosette():
    sc = create_strain_collection()
    sc.add_rosette("R2", {"columns": ["a", "b", "c"]})
    assert sc.get_rosette("R2") is not None

    with pytest.raises(ValueError):
        sc.add_rosette("R3", {"no_columns": True})

def test_strain_collection_properties():
    sc = create_strain_collection()
    assert sc.ops is not None
    # visualization module for strain is apparently not implemented yet
    with pytest.raises(ModuleNotFoundError):
        _ = sc.plot

def test_strain_collection_clone():
    sc = create_strain_collection(
        rosettes={"R1": {"columns": ["a", "b", "c"]}}
    )
    sc2 = sc.clone()
    assert sc2 is not sc
    assert sc2.get_rosette("R1") is not None
