import os
import sys
import pytest
from pathlib import Path

import numpy as np

# テスト実行環境でのtascpyモジュールのインポート設定
# プロジェクトのルートディレクトリをPYTHONPATHに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.core.io.formats import register_format
import tascpy


def load_tasc_file(path, **kwargs):
    return tascpy.load(path, format_name="tasc", **kwargs)


def _write(tmp_path, content, encoding):
    path = tmp_path / "data.txt"
    path.write_text(content, encoding=encoding)
    return path

# テストデータパスの設定
TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))


class TestCollectionFileOperations:
    """ColumnCollectionのファイル操作機能のテスト"""

    # テストデータの定義
    TEST_FILE_CONTENT = """DATA
CH\tDATE\tTIME\tCH1\tCH2\tCH3
NAME\tDATE\tTIME\tForce\tDisplacement\tTemperature
UNIT\t\t\tkN\tmm\t°C
1\t2025/04/29\t10:00:00\t0.5\t0.1\t25.0
2\t2025/04/29\t10:00:01\t1.0\t0.2\t25.1
3\t2025/04/29\t10:00:02\t1.5\t0.3\t25.2
4\t2025/04/29\t10:00:03\t2.0\t0.4\t25.3
5\t2025/04/29\t10:00:04\t2.5\t0.5\t25.4"""

    # CSVテストデータ
    TEST_CSV_CONTENT = """DATA
CH,DATE,TIME,CH1,CH2,CH3
NAME,DATE,TIME,Force,Displacement,Temperature
UNIT,,,kN,mm,°C
1,2025/04/29,10:00:00,0.5,0.1,25.0
2,2025/04/29,10:00:01,1.0,0.2,25.1
3,2025/04/29,10:00:02,1.5,0.3,25.2
4,2025/04/29,10:00:03,2.0,0.4,25.3
5,2025/04/29,10:00:04,2.5,0.5,25.4"""

    # W-N.txtテストデータ
    TEST_WN_CONTENT = """無題
ﾃﾞｰﾀ番号\t日付\t時刻\tCH0\tCH1\tCH2\tCH3
\t\t\tForce1\tForce2\tDisplacement1\tDisplacement2
\t\t\tkN\tkN\tmm\tmm
1\t2020/11/30\t17:21:36\tnone\tnone\tnone\tnone
2\t2020/11/30\t17:29:40\tnone\tnone\tnone\tnone
3\t2020/12/01\t13:22:11\t0.0\t0.0\t0.00\t0.00
4\t2020/12/01\t13:38:05\t2.9\t8.8\t0.08\t0.56
5\t2020/12/01\t13:38:10\t2.9\t8.8\t0.08\t0.61"""


    def test_from_file_standard_format(self, tmp_path):
        """標準フォーマットファイルからの読み込みテスト"""
        collection = tascpy.load(_write(tmp_path, self.TEST_FILE_CONTENT, "utf-8"), format_name="standard")

        assert len(collection) == 5
        assert collection.columns == ["Force", "Displacement", "Temperature"]
        assert collection.step.tolist() == [1, 2, 3, 4, 5]
        assert collection["Force"].values.tolist() == [0.5, 1.0, 1.5, 2.0, 2.5]
        assert collection["Displacement"].values.tolist() == [0.1, 0.2, 0.3, 0.4, 0.5]
        assert collection["Temperature"].values.tolist() == [25.0, 25.1, 25.2, 25.3, 25.4]
        assert [collection[n].ch for n in collection.columns] == ["CH1", "CH2", "CH3"]
        assert collection.units == {"Force": "kN", "Displacement": "mm", "Temperature": "°C"}
        assert collection.date[0] == "2025/04/29"
        assert collection.time[0] == "10:00:00"

    def test_from_file_csv_format(self, tmp_path):
        """CSVフォーマットファイルからの読み込みテスト"""
        collection = tascpy.load(_write(tmp_path, self.TEST_CSV_CONTENT, "utf-8"), format_name="csv")

        assert len(collection) == 5
        assert len(collection.columns) == 3
        assert collection["Force"].values.tolist() == [0.5, 1.0, 1.5, 2.0, 2.5]

    def test_from_file_tasc_format(self, tmp_path):
        """TASC形式（Shift-JIS）ファイルからの読み込みテスト"""
        collection = tascpy.load(_write(tmp_path, self.TEST_WN_CONTENT, "shift_jis"), format_name="tasc")

        assert len(collection) == 5
        assert len(collection.columns) == 4
        assert collection.step.tolist() == [1, 2, 3, 4, 5]
        ch0 = collection.by_ch("CH0")
        assert ch0.name == "Force1"
        assert ch0[0] is None
        assert np.isnan(ch0.values[0])
        assert ch0.values[2] == 0.0
        assert ch0.values[3] == 2.9
        assert collection.date[0] == "2020/11/30"
        assert collection.time[0] == "17:21:36"
        assert collection.by_ch("CH0").unit == "kN"
        assert collection.by_ch("CH2").unit == "mm"

    def test_load_tasc_file(self, tmp_path):
        """format_name="tasc" での読み込み"""
        collection = load_tasc_file(_write(tmp_path, self.TEST_WN_CONTENT, "shift_jis"))

        assert len(collection) == 5
        assert len(collection.columns) == 4
        assert collection.metadata["format"] == "tasc"

    def test_custom_format(self, tmp_path, monkeypatch):
        """カスタムフォーマットでの読み込みテスト"""
        from tascpy.core.io import formats
        monkeypatch.setattr(formats, "FILE_FORMATS", dict(formats.FILE_FORMATS))
        register_format("custom_test", {
            "ch_row": 0, "name_row": 0, "unit_row": 1, "data_start_row": 2,
            "step_col": 0, "date_col": None, "time_col": None, "data_start_col": 1,
        })
        custom_data = "\tCH1\tCH2\tCH3\n\tkN\tmm\t°C\n1\t0.5\t0.1\t25.0\n2\t1.0\t0.2\t25.1\n3\t1.5\t0.3\t25.2"

        collection = tascpy.load(_write(tmp_path, custom_data, "utf-8"), format_name="custom_test")

        assert len(collection) == 3
        assert list(collection.step) == [1, 2, 3]
        assert collection.units == {"CH1": "kN", "CH2": "mm", "CH3": "°C"}

    def test_to_file_standard_format(self, tmp_path):
        """標準フォーマットでのファイル書き出しテスト"""
        columns = {
            "Force": Column("Force", [10.0, 20.0, 30.0], unit="kN", ch="CH1"),
            "Displacement": Column("Displacement", [1.0, 2.0, 3.0], unit="mm", ch="CH2"),
        }
        collection = ColumnCollection(
            columns, step=[1, 2, 3],
            date=["2025/04/29"] * 3, time=["12:00:00", "12:00:01", "12:00:02"],
        )
        path = tmp_path / "output.txt"
        collection.io.save(path, format_name="standard")

        lines = path.read_text(encoding="utf-8").splitlines()
        assert lines[:4] == [
            "DATA",
            "CH\tDATE\tTIME\tCH1\tCH2",
            "NAME\tDATE\tTIME\tForce\tDisplacement",
            "UNIT\t\t\tkN\tmm",
        ]
        assert lines[4] == "1\t2025/04/29\t12:00:00\t10.0\t1.0"

    def test_nonexistent_file(self, tmp_path):
        """存在しないファイルの読み込み時の例外テスト"""
        with pytest.raises(FileNotFoundError):
            tascpy.load(tmp_path / "nonexistent.txt")

    def test_invalid_format(self, tmp_path):
        """無効なフォーマット指定時の例外テスト"""
        with pytest.raises(KeyError):
            tascpy.load(_write(tmp_path, "some test data", "utf-8"), format_name="invalid_format")

    def test_date_time_properties(self, tmp_path):
        """日付・時間はインデックス列として読み込まれる"""
        collection = tascpy.load(_write(tmp_path, self.TEST_FILE_CONTENT, "shift_jis"))

        assert list(collection.date) == ["2025/04/29"] * 5
        assert list(collection.time) == [f"10:00:0{i}" for i in range(5)]
        assert "date" not in collection.columns
        assert "date" not in collection.metadata

    def test_real_tasc_file_load(self, tasc_file):
        """実際のTASC形式（W-N.txt）ファイルを読み込むテスト"""
        # テストデータファイルのパス
        tasc_file_path = str(tasc_file)

        # ファイルが存在することを確認
        assert os.path.exists(
            tasc_file_path
        ), f"テストファイル {tasc_file_path} が見つかりません"

        # TASC形式ファイルの読み込み
        collection = load_tasc_file(tasc_file_path)

        # 基本的な検証
        assert isinstance(
            collection, ColumnCollection
        ), "返されたオブジェクトがColumnCollectionでありません"
        assert len(collection) > 0, "データが読み込まれていません"
        assert len(collection.columns) > 0, "列が読み込まれていません"

        # フォーマットの検証
        assert collection.metadata["format"] == "tasc"

        # データの検証
        # 1行目のデータを検証（1行目はﾃﾞｰﾀ番号が1になっているはず）
        assert collection.step[0] == 1

        assert collection.date[0] == "2020/11/30"
        assert collection.time[0] == "17:21:36"

        # いくつかのカラムをチェック
        ch0 = collection.by_ch("CH0")
        assert ch0[0] is None  # 最初の数行は "none"
        assert ch0[2] == 0.0
        assert ch0.unit == "kN"

        # TASCファイルの特性を確認（"none"値の処理が正しいことを確認）
        assert any(collection[name].null_count() > 0 for name in collection.columns)

    def test_tasc_file_specific_columns(self, tasc_file):
        """TASCファイルから特定の列だけを抽出するテスト"""
        # チャンネル名を使用してファイルを読み込む
        selected_ch_columns = ["CH0", "CH1"]
        collection_ch = load_tasc_file(
            str(tasc_file), selected_columns=selected_ch_columns
        )

        # 指定したチャンネル列だけが読み込まれているか確認
        assert len(collection_ch.columns) == len(selected_ch_columns)
        for name in collection_ch.columns:
            assert collection_ch[name].ch in selected_ch_columns

        # 列名を使用してファイルを読み込む
        # テストデータには、列名が"Force1", "Force2", "Displacement1", "Displacement2"があるはず
        selected_name_columns = ["Force1", "Displacement1"]
        collection_name = load_tasc_file(
            str(tasc_file), selected_columns=selected_name_columns
        )

        # 指定した列名だけが読み込まれているか確認
        assert len(collection_name.columns) == len(selected_name_columns)
        for col_name in selected_name_columns:
            assert (
                col_name in collection_name.columns
            ), f"指定した列 {col_name} が読み込まれていません"

        # 列名とチャンネル名を混合して使用
        mixed_columns = ["CH0", "Displacement1"]
        collection_mixed = load_tasc_file(
            str(tasc_file), selected_columns=mixed_columns
        )

        # 混合指定した列が読み込まれているか確認
        assert len(collection_mixed.columns) == len(mixed_columns)

        # CH0のチャンネル名を持つ列が含まれていることを確認
        assert collection_mixed.by_ch("CH0") is not None

        # Displacement1という列名の列が含まれていることを確認
        assert (
            "Displacement1" in collection_mixed.columns
        ), "指定した列名Displacement1が読み込まれていません"

        # 基本データが正しいことを確認
        assert len(collection_mixed) > 0
        assert collection_mixed.metadata["format"] == "tasc"


    @pytest.mark.parametrize("format_name, encoding, expected", [
        ("tasc", None, "shift_jis"),
        ("standard", None, "utf-8"),
        ("tasc", "euc-jp", "euc-jp"),
    ])
    def test_encoding_settings(self, tmp_path, format_name, encoding, expected):
        """フォーマット（または encoding 指定）に応じたエンコーディングで読み込む"""
        path = _write(tmp_path, self.TEST_FILE_CONTENT.replace("Force", "荷重"), expected)
        kwargs = {"encoding": encoding} if encoding else {}
        collection = tascpy.load(path, format_name=format_name, **kwargs)
        assert collection.columns[0] == "荷重"

    @pytest.mark.parametrize("format_name, encoding, expected", [
        ("tasc", None, "shift_jis"),
        ("standard", None, "utf-8"),
        ("tasc", "euc-jp", "euc-jp"),
    ])
    def test_to_file_with_encoding(self, tmp_path, format_name, encoding, expected):
        """ファイル出力時のエンコーディング設定のテスト"""
        collection = ColumnCollection({"荷重": Column("荷重", [1.0, 2.0, 3.0], unit="kN", ch="T1")}, step=[1, 2, 3])
        path = tmp_path / "output.txt"
        collection.io.save(path, format_name=format_name, encoding=encoding)

        assert "荷重" in path.read_bytes().decode(expected)
        assert tascpy.load(path, format_name=format_name, encoding=expected).columns == ["荷重"]
