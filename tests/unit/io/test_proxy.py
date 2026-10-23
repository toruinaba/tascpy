import pytest
from pathlib import Path
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
import tascpy

@pytest.fixture
def sample_collection():
    return ColumnCollection(
        step=[1, 2, 3],
        columns={
            "A": Column("1", "A", "N", [10, 20, 30]),
            "B": Column("2", "B", "kg", [1.1, 2.2, 3.3])
        }
    )

def test_collection_io_save(sample_collection, tmp_path):
    out_path = tmp_path / "out.txt"
    sample_collection.io.save(out_path)
    assert out_path.exists()

def test_collection_io_to_csv_registered(sample_collection, tmp_path):
    out_path = tmp_path / "out.csv"
    # test registered csv format
    sample_collection.io.to_csv(out_path)
    assert out_path.exists()
