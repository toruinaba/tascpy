import pytest

from tascpy.domains import StrainOps
from tascpy.core.collection import ColumnCollection
from tascpy.domains.strain import StrainCollection
from tascpy.domains.strain.plotter import StrainPlotter
from tascpy.domains import as_strain

ROSETTE = {"columns": ["ch1", "ch2", "ch3"], "type": "rectangular", "orientation": 0.0}


def test_strain_collection_init():
    sc = StrainCollection({"ch1": [1, 2, 3]}, step=[1, 2, 3], rosettes={"R1": ROSETTE})
    assert sc.domain == "strain"
    assert sc.get_rosette("R1") == ROSETTE
    assert sc.rosettes == {"R1": ROSETTE}


def test_strain_collection_init_with_coordinates():
    sc = StrainCollection({"ch1": [1, 2, 3]}, coordinates={"ch1": {"x": 1.0, "y": 2.0}})
    assert sc.get_column_coordinates("ch1") == (1.0, 2.0, None)


def test_strain_collection_with_rosette():
    sc = StrainCollection()
    sc2 = sc.with_rosette("R2", {"columns": ["a", "b", "c"]})
    assert sc2.get_rosette("R2") is not None
    assert sc.get_rosette("R2") is None

    with pytest.raises(ValueError):
        sc.with_rosette("R3", {"no_columns": True})


def test_strain_collection_invalid_rosette_on_init():
    with pytest.raises(ValueError):
        StrainCollection(rosettes={"R": {"type": "rectangular"}})


def test_strain_collection_properties():
    sc = StrainCollection()
    assert isinstance(sc.ops, StrainOps)
    assert isinstance(sc.plot, StrainPlotter)


def test_rosettes_survive_operations():
    sc = StrainCollection({"a": [1.0, 2.0]}, rosettes={"R1": {"columns": ["a", "b", "c"]}})
    result = sc.ops.add("a", 1.0, result_column="b").end()
    assert isinstance(result, StrainCollection)
    assert result.get_rosette("R1") is not None


def test_from_collection():
    base = ColumnCollection({"ch1": [1.0], "ch2": [2.0], "ch3": [3.0]})
    sc = base.ops.as_domain(as_strain, rosettes={"R1": ROSETTE}, coordinates={"ch1": {"x": 0.0, "y": 1.0}}).end()
    assert isinstance(sc, StrainCollection)
    assert sc.get_rosette("R1") == ROSETTE
    assert sc.get_column_coordinates("ch1") == (0.0, 1.0, None)
