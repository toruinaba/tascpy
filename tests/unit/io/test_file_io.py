from pathlib import Path
import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.io.file_io import load_collection, save_collection
import tascpy

@pytest.fixture
def sample_data_path(tmp_path):
    # tasc_txtはデフォルトでタブ区切り
    # col 0: Step, col 1: Date, col 2: Time, col 3+: Data
    data = "DATA\nCH\tDATE\tTIME\tCH1\tCH2\nNAME\tDATE\tTIME\tForce\tDisplacement\nUNIT\t\ts\tkN\tmm\n1\t2023/01/01\t00:00:00\t0.0\t0.0\n2\t2023/01/01\t00:00:01\t1.5\t0.5\n3\t2023/01/01\t00:00:02\t3.0\t1.0\n4\t2023/01/01\t00:00:03\t4.5\t1.5\n5\t2023/01/01\t00:00:04\t6.0\t2.0\n"
    file_path = tmp_path / "test_data.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data)
    return file_path

def test_load_collection(sample_data_path):
    """load_collection関数のテスト"""
    collection = load_collection(sample_data_path)
    
    assert isinstance(collection, ColumnCollection)
    assert len(collection) == 5
    assert "Force" in collection.columns
    assert "Displacement" in collection.columns
    np.testing.assert_allclose(collection["Force"].values, [0.0, 1.5, 3.0, 4.5, 6.0])
    assert collection.units == {"Force": "kN", "Displacement": "mm"}
    assert collection["Force"].ch == "CH1"
    assert list(collection.time)[:2] == ["00:00:00", "00:00:01"]
    assert collection.metadata["source"] == str(sample_data_path)

def test_save_collection(tmp_path):
    """save_collection関数のテスト"""
    # データ作成
    from tascpy.core.column import Column

    columns = {
        "A": Column("A", [10, 20, 30], unit="u1", ch="CH1"),
        "B": Column("B", [1.1, 2.2, 3.3], unit="u2", ch="CH2"),
    }
    collection = ColumnCollection(columns, step=[1, 2, 3])
    
    output_path = tmp_path / "output.txt"
    save_collection(collection, output_path)

    loaded = load_collection(output_path)
    assert loaded.columns == ["A", "B"]
    assert loaded.meta == collection.meta
    np.testing.assert_array_equal(loaded["A"].values, [10, 20, 30])
    np.testing.assert_allclose(loaded["B"].values, [1.1, 2.2, 3.3])
    np.testing.assert_array_equal(loaded.step, [1, 2, 3])
    assert loaded.df.equals(collection.df)

def test_selected_columns(sample_data_path):
    collection = tascpy.load(sample_data_path, selected_columns=["Force"])
    assert collection.columns == ["Force"]
    by_ch = tascpy.io.load(sample_data_path, selected_columns=["CH2"])
    assert by_ch.columns == ["Displacement"]

def test_public_load_and_save_roundtrip(sample_data_path, tmp_path):
    """tascpy.load / collection.io.save による読み書き"""
    collection = tascpy.load(sample_data_path)
    assert len(collection) == 5

    # to_file
    output_path = tmp_path / "legacy_output.txt"
    collection.io.save(output_path)
    assert output_path.exists()
    
    # 確認
    reloaded = tascpy.io.load(output_path)
    assert len(reloaded) == 5
    assert list(reloaded.units.values()) == list(collection.units.values())
    assert list(reloaded.date) == list(collection.date)
    assert reloaded.columns == collection.columns
    assert reloaded.meta == collection.meta
    np.testing.assert_allclose(reloaded["Force"].values, collection["Force"].values)
