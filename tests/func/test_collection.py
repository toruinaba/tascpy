import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, call

import numpy as np

# テスト実行環境でのtascpyモジュールのインポート設定
# プロジェクトのルートディレクトリをPYTHONPATHに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column
from src.tascpy.core.io_formats import register_format
from src.tascpy.io.file_handlers import load_from_file, save_to_file, load_tasc_file

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

    def test_from_file_standard_format(self):
        """標準フォーマットファイルからの読み込みテスト"""
        # mock_openを使用してファイル
        with patch("builtins.open", mock_open(read_data=self.TEST_FILE_CONTENT)):
            # Pathオブジェクトの存在チェックをパッチ
            with patch.object(Path, "exists", return_value=True):
                # ダミーのファイルパスでテスト - 明示的に標準フォーマットを指定
                collection = ColumnCollection.from_file(
                    "dummy_path.txt", format_name="standard"
                )

                # 基本構造の検証
                assert len(collection) == 5
                assert len(collection.columns) == 3
                assert list(collection.columns.keys()) == [
                    "Force",
                    "Displacement",
                    "Temperature",
                ]

                # ステップ値の検証
                assert collection.step.values == [1, 2, 3, 4, 5]

                # カラム値の検証
                assert collection["Force"].values == [0.5, 1.0, 1.5, 2.0, 2.5]
                assert collection["Displacement"].values == [0.1, 0.2, 0.3, 0.4, 0.5]
                assert collection["Temperature"].values == [
                    25.0,
                    25.1,
                    25.2,
                    25.3,
                    25.4,
                ]

                # チャンネル情報の検証
                assert collection["Force"].ch == "CH1"
                assert collection["Displacement"].ch == "CH2"
                assert collection["Temperature"].ch == "CH3"

                # 単位の検証
                assert collection["Force"].unit == "kN"
                assert collection["Displacement"].unit == "mm"
                assert collection["Temperature"].unit == "°C"

                # メタデータの検証
                assert "date" in collection.metadata
                assert "time" in collection.metadata
                assert collection.metadata["date"][0] == "2025/04/29"
                assert collection.metadata["time"][0] == "10:00:00"

    def test_from_file_csv_format(self):
        """CSVフォーマットファイルからの読み込みテスト"""
        # mock_openを使用してCSVファイル読み込みをモック
        with patch("builtins.open", mock_open(read_data=self.TEST_CSV_CONTENT)):
            # Pathオブジェクトの存在チェックをパッチ
            with patch.object(Path, "exists", return_value=True):
                # CSVフォーマット指定でテスト
                collection = ColumnCollection.from_file(
                    "dummy_path.csv", format_name="csv"
                )

                # 基本構造の検証
                assert len(collection) == 5
                assert len(collection.columns) == 3

                # データ値の検証
                assert collection["Force"].values == [0.5, 1.0, 1.5, 2.0, 2.5]

    def test_from_file_tasc_format(self):
        """TASC形式（以前のW-N.txt形式）ファイルからの読み込みテスト"""
        # mock_openを使用してTASCファイル読み込みをモック
        with patch("builtins.open", mock_open(read_data=self.TEST_WN_CONTENT)):
            # Pathオブジェクトの存在チェックをパッチ
            with patch.object(Path, "exists", return_value=True):
                # TASC形式指定でテスト
                collection = ColumnCollection.from_file(
                    "dummy_path.txt", format_name="tasc"
                )

                # 基本構造の検証
                assert len(collection) == 5
                assert len(collection.columns) == 4

                # ステップ値の検証
                assert collection.step.values == [1, 2, 3, 4, 5]

                # カラム値の検証（None値も含む）
                assert collection["CH0"].values[0] is None
                assert collection["CH0"].values[2] == 0.0
                assert collection["CH0"].values[3] == 2.9

                # 日付と時刻の検証
                assert collection.metadata["date"][0] == "2020/11/30"
                assert collection.metadata["time"][0] == "17:21:36"

                # 単位の検証
                assert collection["CH0"].unit == "kN"
                assert collection["CH2"].unit == "mm"

    def test_load_tasc_file(self):
        """load_tasc_file関数のテスト"""
        # mock_openを使用してTASCファイル読み込みをモック
        with patch("builtins.open", mock_open(read_data=self.TEST_WN_CONTENT)):
            # Pathオブジェクトの存在チェックをパッチ
            with patch.object(Path, "exists", return_value=True):
                # 専用ローダー関数でテスト
                collection = load_tasc_file("dummy_path.txt")

                # 基本構造の検証
                assert len(collection) == 5
                assert len(collection.columns) == 4

                # フォーマットの検証
                assert collection.metadata["format"] == "tasc"

    def test_custom_format(self):
        """カスタムフォーマットでの読み込みテスト"""
        # カスタムフォーマット定義
        custom_format = {
            "delimiter": "\t",
            "title_row": None,  # タイトル行なし
            "ch_row": 0,
            "name_row": 0,
            "unit_row": 1,
            "data_start_row": 2,
            "step_col": 0,
            "date_col": None,  # 日付なし
            "time_col": None,  # 時間なし
            "data_start_col": 1,  # 最初の列はステップ、その次からデータ
        }

        # カスタムテストデータ - 修正版（カラムが3つになるようにする）
        custom_data = """\tCH1\tCH2\tCH3
\tkN\tmm\t°C
1\t0.5\t0.1\t25.0
2\t1.0\t0.2\t25.1
3\t1.5\t0.3\t25.2"""

        # カスタムフォーマットを登録
        register_format("custom_test", custom_format)

        # mock_openを使用
        with patch("builtins.open", mock_open(read_data=custom_data)):
            with patch.object(Path, "exists", return_value=True):
                # カスタムフォーマットで読み込み
                collection = ColumnCollection.from_file(
                    "dummy_path.txt", format_name="custom_test"
                )

                # デバッグ情報の表示
                print(f"カラム名: {list(collection.columns.keys())}")
                print(f"カラム数: {len(collection.columns)}")

                # 検証
                assert len(collection) == 3  # 3行
                assert len(collection.columns) == 3  # 3列
                assert list(collection.step.values) == [1, 2, 3]  # ステップ値

    def test_to_file_standard_format(self):
        """標準フォーマットでのファイル書き出しテスト"""
        # テスト用のCollectionを作成
        steps = [1, 2, 3]
        columns = {
            "Force": Column("CH1", "Force", "kN", [10.0, 20.0, 30.0]),
            "Displacement": Column("CH2", "Displacement", "mm", [1.0, 2.0, 3.0]),
        }
        metadata = {
            "date": ["2025/04/29"] * 3,
            "time": ["12:00:00", "12:00:01", "12:00:02"],
        }

        collection = ColumnCollection(steps, columns, metadata)

        # ファイル書き込みをモック
        m = mock_open()
        with patch("builtins.open", m):
            # 標準フォーマット明示的に指定
            collection.to_file("output.txt", format_name="standard")

            # 書き込み呼び出しの検証
            m.assert_called_once_with(Path("output.txt"), "w", encoding="utf-8")

            # 書き込まれた内容の検証（一部）
            handle = m()
            assert handle.write.called

            # 出力された内容にヘッダー情報が含まれていることを確認
            calls = [call[0][0] for call in handle.write.call_args_list]
            assert any("DATA" in call for call in calls)
            assert any("CH\tDATE\tTIME\tCH1\tCH2" in call for call in calls)
            assert any(
                "NAME\tDATE\tTIME\tForce\tDisplacement" in call for call in calls
            )

    def test_file_handlers(self):
        """io.file_handlersモジュールのテスト"""
        # テスト用のCollectionを作成
        steps = [1, 2]
        columns = {"Test": Column("T1", "Test", "", [1.0, 2.0])}
        collection = ColumnCollection(steps, columns)

        # load_from_fileのテスト - モックパスを修正
        with patch(
            "src.tascpy.core.collection.ColumnCollection.from_file"
        ) as mock_from_file:
            load_from_file("test.txt")
            mock_from_file.assert_called_once()

        # save_to_fileのテスト
        with patch(
            "src.tascpy.core.collection.ColumnCollection.to_file"
        ) as mock_to_file:
            save_to_file(collection, "test.txt")
            mock_to_file.assert_called_once()

    def test_nonexistent_file(self):
        """存在しないファイルの読み込み時の例外テスト"""
        with patch.object(Path, "exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                ColumnCollection.from_file("nonexistent.txt")

    def test_invalid_format(self):
        """無効なフォーマット指定時の例外テスト"""
        # 適切なモックデータを提供
        mock_data = "some test data"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            with patch.object(Path, "exists", return_value=True):
                with pytest.raises(KeyError):
                    ColumnCollection.from_file("test.txt", format_name="invalid_format")

    def test_date_time_properties(self):
        """日付・時間プロパティのテスト"""
        # mock_openを使用してファイル読み込みをモック
        with patch("builtins.open", mock_open(read_data=self.TEST_FILE_CONTENT)):
            with patch.object(Path, "exists", return_value=True):
                collection = ColumnCollection.from_file("dummy_path.txt")

                # 日付・時間プロパティの検証
                assert collection.date == collection.metadata["date"]
                assert collection.time == collection.metadata["time"]

                # get_date_timeメソッドの検証
                date, time = collection.get_date_time()
                assert date == collection.date
                assert time == collection.time

    def test_real_tasc_file_load(self):
        """実際のTASC形式（W-N.txt）ファイルを読み込むテスト"""
        # テストデータファイルのパス
        tasc_file_path = os.path.join(TEST_DATA_DIR, "W-N.txt")

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
        assert (
            collection.step.values[0] == 1
        ), f"最初のステップ値が1ではありません：{collection.step.values[0]}"

        # 日付と時間のメタデータが存在することを確認
        assert "date" in collection.metadata
        assert "time" in collection.metadata
        assert (
            collection.metadata["date"][0] == "2020/11/30"
        ), f"最初の日付が期待値と異なります：{collection.metadata['date'][0]}"
        assert (
            collection.metadata["time"][0] == "17:21:36"
        ), f"最初の時刻が期待値と異なります：{collection.metadata['time'][0]}"

        # いくつかのカラムをチェック
        if "CH0" in collection.columns:
            # CH0は最初の数行に"none"値があるはず
            assert (
                collection["CH0"].values[0] is None
            ), "CH0の最初の値がNoneではありません"
            # 5行目（インデックス4）以降には数値があるはず
            assert (
                collection["CH0"].values[4] == 0.0
            ), f"CH0の5行目の値が0.0ではありません：{collection['CH0'].values[4]}"

        # 単位が正しく読み込まれているか確認
        if "CH0" in collection.columns:
            assert (
                collection["CH0"].unit == "kN"
            ), f"CH0の単位がkNではありません：{collection['CH0'].unit}"

        # TASCファイルの特性を確認（"none"値の処理が正しいことを確認）
        none_values_exist = False
        for col_name, column in collection.columns.items():
            if any(val is None for val in column.values):
                none_values_exist = True
                break
        assert none_values_exist, '"none"値が正しく変換されていません'

        print(f"読み込まれた列数: {len(collection.columns)}")
        print(f"読み込まれた行数: {len(collection)}")
        print(f"最初の5つの列名: {list(collection.columns.keys())[:5]}")

    def test_tasc_file_specific_columns(self):
        """TASCファイルから特定の列だけを抽出するテスト"""
        # mock_openを使用してTASCファイル読み込みをモック
        with patch("builtins.open", mock_open(read_data=self.TEST_WN_CONTENT)):
            # Pathオブジェクトの存在チェックをパッチ
            with patch.object(Path, "exists", return_value=True):
                # チャンネル名を使用してファイルを読み込む
                selected_ch_columns = ["CH0", "CH1"]
                collection_ch = load_tasc_file(
                    "dummy_path.txt", selected_columns=selected_ch_columns
                )

                # 指定したチャンネル列だけが読み込まれているか確認
                assert len(collection_ch.columns) == len(selected_ch_columns)
                for col in collection_ch.columns.values():
                    assert (
                        col.ch in selected_ch_columns
                    ), f"指定したチャンネル {col.ch} が読み込まれていません"

                # 他のチャンネル列が含まれていないことを確認
                for col in collection_ch.columns.values():
                    assert (
                        col.ch in selected_ch_columns
                    ), f"指定していないチャンネル {col.ch} が読み込まれています"

                # 列名を使用してファイルを読み込む
                # テストデータには、列名が"Force1", "Force2", "Displacement1", "Displacement2"があるはず
                selected_name_columns = ["Force1", "Displacement1"]
                collection_name = load_tasc_file(
                    "dummy_path.txt", selected_columns=selected_name_columns
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
                    "dummy_path.txt", selected_columns=mixed_columns
                )

                # 混合指定した列が読み込まれているか確認
                assert len(collection_mixed.columns) == len(mixed_columns)

                # CH0のチャンネル名を持つ列が含まれていることを確認
                ch0_exists = False
                for col in collection_mixed.columns.values():
                    if col.ch == "CH0":
                        ch0_exists = True
                        break
                assert ch0_exists, "指定したチャンネルCH0の列が読み込まれていません"

                # Displacement1という列名の列が含まれていることを確認
                assert (
                    "Displacement1" in collection_mixed.columns
                ), "指定した列名Displacement1が読み込まれていません"

                # 基本データが正しいことを確認
                assert len(collection_mixed) > 0
                assert collection_mixed.metadata["format"] == "tasc"

    def test_encoding_settings(self):
        """ファイルフォーマットのエンコーディング設定のテスト"""
        with patch.object(Path, "exists", return_value=True):
            # TASCフォーマットを使用すると自動的にShift-JISエンコーディングになるはず
            with patch(
                "builtins.open", mock_open(read_data="テストデータ")
            ) as mock_file:
                with patch(
                    "src.tascpy.core.collection.open", mock_file
                ) as mock_open_func:
                    # ここでは実際にファイルを読み込む必要はない、エンコーディング設定が正しく渡されたかだけを確認
                    ColumnCollection.from_file("dummy_path.txt", format_name="tasc")
                    # openが呼び出されたか確認
                    mock_file.assert_called()
                    # 引数をチェック（エンコーディングがshift_jisかどうか）
                    call_args = mock_file.call_args_list[0]
                    assert call_args[1]["encoding"] == "shift_jis"

            # 標準フォーマットならUTF-8になるはず
            with patch(
                "builtins.open", mock_open(read_data="テストデータ")
            ) as mock_file:
                with patch("src.tascpy.core.collection.open", mock_file):
                    ColumnCollection.from_file("dummy_path.txt", format_name="standard")
                    # 引数をチェック
                    call_args = mock_file.call_args_list[0]
                    assert call_args[1]["encoding"] == "utf-8"

            # 明示的にエンコーディングを指定した場合、それが使われるはず
            with patch(
                "builtins.open", mock_open(read_data="テストデータ")
            ) as mock_file:
                with patch("src.tascpy.core.collection.open", mock_file):
                    ColumnCollection.from_file(
                        "dummy_path.txt",
                        format_name="tasc",
                        encoding="euc-jp",  # エンコーディングを上書き
                    )
                    # 引数をチェック
                    call_args = mock_file.call_args_list[0]
                    assert call_args[1]["encoding"] == "euc-jp"

    def test_to_file_with_encoding(self):
        """ファイル出力時のエンコーディング設定のテスト"""
        # テスト用のCollectionを作成
        steps = [1, 2, 3]
        columns = {"Test": Column("T1", "Test", "unit", [1.0, 2.0, 3.0])}
        collection = ColumnCollection(steps, columns)

        # TASCフォーマットでの保存（Shift-JIS）
        with patch("src.tascpy.core.collection.open") as mock_open_func:
            collection.to_file("output.txt")  # デフォルトはtasc
            # 適切なエンコーディングが使われているか確認
            mock_open_func.assert_called_with(
                Path("output.txt"), "w", encoding="shift_jis"
            )

        # 標準フォーマットでの保存（UTF-8）
        with patch("src.tascpy.core.collection.open") as mock_open_func:
            collection.to_file("output.txt", format_name="standard")
            # 適切なエンコーディングが使われているか確認
            mock_open_func.assert_called_with(Path("output.txt"), "w", encoding="utf-8")

        # カスタムエンコーディングでの保存
        with patch("src.tascpy.core.collection.open") as mock_open_func:
            collection.to_file("output.txt", encoding="euc-jp")
            # 指定したエンコーディングが使われているか確認
            mock_open_func.assert_called_with(
                Path("output.txt"), "w", encoding="euc-jp"
            )
