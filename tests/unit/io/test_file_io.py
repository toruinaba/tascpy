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
    assert collection.metadata["source"] == str(sample_data_path)

def test_save_collection(tmp_path):
    """save_collection関数のテスト"""
    # データ作成
    from tascpy.core.column import Column
    from tascpy.core.step import Step
    
    step = Step([1, 2, 3])
    columns = {
        "A": Column("CH1", "A", "u1", [10, 20, 30]),
        "B": Column("CH2", "B", "u2", [1.1, 2.2, 3.3])
    }
    collection = ColumnCollection(step, columns)
    
    output_path = tmp_path / "output.txt"
    # format_name="tasc_txt" (デフォルト) は use_channel_name=True なので、
    # 保存時にName行にチャンネル名(CH1, CH2)が書き込まれる
    save_collection(collection, output_path)
    
    assert output_path.exists()
    
    # 読み込んで確認
    loaded = load_collection(output_path)
    assert len(loaded) == 3
    # 保存時の挙動により、キーがCH1, CH2になっていることを確認
    np.testing.assert_array_equal(loaded["CH1"].values, [10, 20, 30])
    np.testing.assert_allclose(loaded["CH2"].values, [1.1, 2.2, 3.3])

def test_legacy_compatibility(sample_data_path, tmp_path):
    """ColumnCollectionのクラスメソッド経由での互換性テスト"""
    # from_file
    collection = tascpy.io.load(sample_data_path)
    assert len(collection) == 5
    
    # to_file
    output_path = tmp_path / "legacy_output.txt"
    collection.io.save(output_path)
    assert output_path.exists()
    
    # 確認
    reloaded = tascpy.io.load(output_path)
    assert len(reloaded) == 5
