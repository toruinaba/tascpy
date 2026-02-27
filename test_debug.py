import pytest
from tascpy.core.collection import ColumnCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.operations.load_displacement.analysis import calculate_stiffness

def test_debug():
    steps = list(range(11))
    loads = [0, 10, 20, 30, 40, 50, 55, 60, 63, 65, 66]
    disps = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    collection = ColumnCollection(steps, {"load": loads, "displacement": disps})
    ld_collection = LoadDisplacementCollection(
        step=collection.step,
        columns=collection.columns,
        load_column="load",
        displacement_column="displacement",
    )
    calculate_stiffness(ld_collection, range_start=0.2)

test_debug()
