import pytest
from pathlib import Path
from tascpy.io.file_handlers import load_from_file, save_to_file, load_tasc_file
from tascpy.core.collection import ColumnCollection
import numpy as np

@pytest.fixture
def sample_data_path(tmp_path):
    data = "DATA\nCH\tDATE\tTIME\tCH1\nNAME\tDATE\tTIME\tForce\nUNIT\t\ts\tkN\n1\t2023/01/01\t00:00:00\t0.0\n2\t2023/01/01\t00:00:01\t1.5\n"
    file_path = tmp_path / "test_handler_data.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data)
    return file_path

def test_load_from_file(sample_data_path):
    collection = load_from_file(sample_data_path)
    assert isinstance(collection, ColumnCollection)
    assert len(collection) == 2
    assert "Force" in collection.columns

def test_load_tasc_file(sample_data_path):
    collection = load_tasc_file(sample_data_path)
    assert isinstance(collection, ColumnCollection)
    assert len(collection) == 2

def test_save_to_file(sample_data_path, tmp_path):
    collection = load_from_file(sample_data_path)
    
    out_path = tmp_path / "out_handler.txt"
    save_to_file(collection, out_path)
    assert out_path.exists()
    
    loaded = load_from_file(out_path)
    assert len(loaded) == 2
