import pytest
from pathlib import Path
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
import tascpy

@pytest.fixture
def sample_collection():
    return ColumnCollection(
        {
            "A": Column("A", [10, 20, 30], unit="N", ch="1"),
            "B": Column("B", [1.1, 2.2, 3.3], unit="kg", ch="2"),
        },
        step=[1, 2, 3],
    )

def test_collection_io_save(sample_collection, tmp_path):
    out_path = tmp_path / "out.txt"
    sample_collection.io.save(out_path)
    assert out_path.exists()

def test_collection_io_to_csv_is_plain_csv(sample_collection, tmp_path):
    import polars as pl
    out_path = tmp_path / "out.csv"
    sample_collection.io.to_csv(out_path)
    assert out_path.read_text().splitlines()[0] == "step,A,B"
    assert pl.read_csv(out_path).equals(sample_collection.df.with_columns(pl.col("step")))


def test_collection_io_save_csv_format_keeps_units(sample_collection, tmp_path):
    out_path = tmp_path / "out.csv"
    sample_collection.io.save(out_path, format_name="csv")
    loaded = tascpy.load(out_path, format_name="csv")
    assert loaded.columns == ["A", "B"]
    assert loaded.units == {"A": "N", "B": "kg"}


def test_collection_io_to_parquet(sample_collection, tmp_path):
    out_path = tmp_path / "out.parquet"
    sample_collection.io.to_parquet(out_path)
    loaded = tascpy.load_parquet(out_path)
    assert loaded.meta == sample_collection.meta
    assert loaded.df.equals(sample_collection.df)
