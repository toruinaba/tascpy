import pytest
from src.tascpy.core.column import (
    Column,
    NumberColumn,
    StringColumn,
    InvalidColumn,
    detect_column_type,
    create_column_from_values,
)
from src.tascpy.core.collection import ColumnCollection
import unittest.mock as mock


class TestColumnTypes:
    """各カラム型のテストクラス"""

    def test_number_column_creation(self):
        """NumberColumnの作成テスト"""
        # 正常なケース
        column = NumberColumn("ch1", "temperature", "°C", [1, 2.5, None, 3])
        assert column.ch == "ch1"
        assert column.name == "temperature"
        assert column.unit == "°C"
        assert column.values == [1, 2.5, None, 3]

        # エラーケース - 文字列が含まれる
        with pytest.raises(TypeError):
            NumberColumn("ch1", "temperature", "°C", [1, "2", None, 3])

        # エラーケース - リストが含まれる
        with pytest.raises(TypeError):
            NumberColumn("ch1", "temperature", "°C", [1, [2, 3], None])

    def test_string_column_creation(self):
        """StringColumnの作成テスト"""
        # 正常なケース
        column = StringColumn("ch2", "status", "", ["OK", None, "Error"])
        assert column.ch == "ch2"
        assert column.name == "status"
        assert column.unit == ""
        assert column.values == ["OK", None, "Error"]

        # エラーケース - 数値が含まれる
        with pytest.raises(TypeError):
            StringColumn("ch2", "status", "", ["OK", 123, None])

        # エラーケース - 辞書が含まれる
        with pytest.raises(TypeError):
            StringColumn("ch2", "status", "", ["OK", {"key": "value"}, None])

    def test_invalid_column_creation(self):
        """InvalidColumnの作成テスト"""
        # 正常なケース - すべてNone
        column = InvalidColumn("ch3", "empty", "", [None, None, None])
        assert column.ch == "ch3"
        assert column.name == "empty"
        assert column.unit == ""
        assert all(v is None for v in column.values)

        # エラーケース - None以外の値を含む
        with pytest.raises(ValueError):
            InvalidColumn("ch3", "empty", "", [None, 1, None])

        # エラーケース - 空の文字列を含む
        with pytest.raises(ValueError):
            InvalidColumn("ch3", "empty", "", [None, "", None])

    def test_column_clone(self):
        """各カラム型のclone()メソッドのテスト"""
        # NumberColumnのクローン
        num_col = NumberColumn("ch1", "temp", "°C", [1, 2.5, None, 3])
        num_clone = num_col.clone()
        assert isinstance(num_clone, NumberColumn)
        assert num_clone is not num_col
        assert num_clone.values == num_col.values
        assert num_clone.values is not num_col.values  # ディープコピーの確認

        # StringColumnのクローン
        str_col = StringColumn("ch2", "status", "", ["OK", None, "Error"])
        str_clone = str_col.clone()
        assert isinstance(str_clone, StringColumn)
        assert str_clone is not str_col
        assert str_clone.values == str_col.values
        assert str_clone.values is not str_col.values

        # InvalidColumnのクローン
        inv_col = InvalidColumn("ch3", "empty", "", [None, None, None])
        inv_clone = inv_col.clone()
        assert isinstance(inv_clone, InvalidColumn)
        assert inv_clone is not inv_col
        assert inv_clone.values == inv_col.values
        assert inv_clone.values is not inv_col.values


class TestNoneHandling:
    """None値処理のテストクラス"""

    def test_count_nones(self):
        """count_nones()メソッドのテスト"""
        # NumberColumnでのテスト
        num_col = NumberColumn("ch1", "temp", "°C", [1, None, 3, None])
        assert num_col.count_nones() == 2

        # StringColumnでのテスト
        str_col = StringColumn("ch2", "status", "", [None, "OK", None])
        assert str_col.count_nones() == 2

        # InvalidColumnでのテスト
        inv_col = InvalidColumn("ch3", "empty", "", [None, None, None])
        assert inv_col.count_nones() == 3

        # 空のカラムでのテスト
        empty_col = Column("ch4", "empty", "", [])
        assert empty_col.count_nones() == 0

        # Noneを含まないカラムでのテスト
        no_none_col = NumberColumn("ch5", "non_empty", "", [1, 2, 3])
        assert no_none_col.count_nones() == 0

    def test_none_indices(self):
        """none_indices()メソッドのテスト"""
        # NumberColumnでのテスト
        num_col = NumberColumn("ch1", "temp", "°C", [1, None, 3, None, 5])
        assert num_col.none_indices() == [1, 3]

        # StringColumnでのテスト
        str_col = StringColumn("ch2", "status", "", ["A", None, "B", "C", None, None])
        assert str_col.none_indices() == [1, 4, 5]

        # InvalidColumnでのテスト
        inv_col = InvalidColumn("ch3", "empty", "", [None, None, None])
        assert inv_col.none_indices() == [0, 1, 2]

        # Noneを含まないカラムでのテスト
        no_none_col = StringColumn("ch4", "non_empty", "", ["A", "B", "C"])
        assert no_none_col.none_indices() == []

        # 空のカラムでのテスト
        empty_col = Column("ch5", "empty", "", [])
        assert empty_col.none_indices() == []

    def test_has_none(self):
        """has_none()メソッドのテスト"""
        # Noneを含む場合
        num_col = NumberColumn("ch1", "temp", "°C", [1, None, 3])
        assert num_col.has_none() is True

        # Noneを含まない場合
        num_col2 = NumberColumn("ch1", "temp", "°C", [1, 2, 3])
        assert num_col2.has_none() is False

        # すべてNoneの場合（InvalidColumn）
        inv_col = InvalidColumn("ch3", "empty", "", [None, None])
        assert inv_col.has_none() is True

        # 空のカラムの場合
        empty_col = Column("ch4", "empty", "", [])
        assert empty_col.has_none() is False


class TestTypeDetection:
    """型検出機能のテストクラス"""

    def test_detect_column_type_numeric(self):
        """数値型検出のテスト"""
        # 整数のみの場合
        column = detect_column_type("ch1", "temp", "°C", [1, 2, 3])
        assert isinstance(column, NumberColumn)

        # 浮動小数点のみの場合
        column = detect_column_type("ch1", "temp", "°C", [1.1, 2.2, 3.3])
        assert isinstance(column, NumberColumn)

        # 整数と浮動小数点の混合
        column = detect_column_type("ch1", "temp", "°C", [1, 2.5, 3])
        assert isinstance(column, NumberColumn)

        # 数値とNoneの混合
        column = detect_column_type("ch1", "temp", "°C", [1, None, 3.5, None])
        assert isinstance(column, NumberColumn)

    def test_detect_column_type_string(self):
        """文字列型検出のテスト"""
        # 文字列のみ
        column = detect_column_type("ch2", "status", "", ["OK", "Error", "Success"])
        assert isinstance(column, StringColumn)

        # 文字列とNoneの混合
        column = detect_column_type("ch2", "status", "", ["OK", None, "Error", None])
        assert isinstance(column, StringColumn)

        # 空の文字列を含む
        column = detect_column_type("ch2", "status", "", ["OK", "", "Error"])
        assert isinstance(column, StringColumn)

    def test_detect_column_type_invalid(self):
        """無効カラムの検出テスト"""
        # すべてNone
        column = detect_column_type("ch3", "empty", "", [None, None, None])
        assert isinstance(column, InvalidColumn)

        # 空のリスト
        column = detect_column_type("ch3", "empty", "", [])
        assert not isinstance(column, InvalidColumn)  # 空のリストは無効カラムではない
        assert isinstance(column, Column)

    def test_detect_column_type_mixed(self):
        """混合型の検出テスト"""
        # 数値と文字列の混合
        column = detect_column_type("ch4", "mixed", "", [1, "text", 3])
        assert not isinstance(column, NumberColumn)
        assert not isinstance(column, StringColumn)
        assert isinstance(column, Column)  # 基本のColumnになる

        # 数値、文字列、None、リスト、辞書などの混合
        column = detect_column_type(
            "ch4", "mixed", "", [1, "text", None, [1, 2], {"a": 1}]
        )
        assert isinstance(column, Column)

    def test_create_column_from_values(self):
        """create_column_from_values関数のテスト"""
        # 型を明示的に指定 - 数値型
        column = create_column_from_values(
            "ch1", "temp", "°C", [1, 2, 3], column_type="number"
        )
        assert isinstance(column, NumberColumn)

        # 数値データでも文字列型を指定すると文字列として扱う（エラーになる）
        with pytest.raises(TypeError):
            create_column_from_values("ch2", "ids", "", [1, 2, 3], column_type="string")

        # 文字列データに数値型を指定するとエラーになる
        with pytest.raises(TypeError):
            create_column_from_values(
                "ch3", "status", "", ["A", "B", "C"], column_type="number"
            )

        # InvalidColumnを明示的に指定
        column = create_column_from_values(
            "ch4", "empty", "", [None, None], column_type="invalid"
        )
        assert isinstance(column, InvalidColumn)

        # 無効な型名を指定した場合は標準のColumnを返す
        column = create_column_from_values(
            "ch5", "data", "", [1, 2, 3], column_type="unknown_type"
        )
        assert type(column) == Column

        # 型を指定しない場合は自動判定
        column = create_column_from_values("ch6", "temp", "°C", [1, 2, 3])
        assert isinstance(column, NumberColumn)

        column = create_column_from_values("ch7", "status", "", ["OK", "Error"])
        assert isinstance(column, StringColumn)


class TestColumnCollectionAutoDetection:
    """ColumnCollectionの自動判定機能のテスト"""

    def test_column_collection_auto_detect_init(self):
        """初期化時の自動判定テスト"""
        # 初期化時に自動判定
        columns = {
            "temp": [1, 2, 3, None],
            "status": ["OK", "Error", "OK", None],
            "empty": [None, None, None, None],
            "mixed": [1, "Error", 3, 4],
        }
        collection = ColumnCollection([1, 2, 3, 4], columns, auto_detect_types=True)

        # 自動判定の結果を検証
        assert isinstance(collection.columns["temp"], NumberColumn)
        assert isinstance(collection.columns["status"], StringColumn)
        assert isinstance(collection.columns["empty"], InvalidColumn)
        assert type(collection.columns["mixed"]) == Column  # 混在型は基本のColumn

        # 自動判定を無効にした場合
        collection2 = ColumnCollection([1, 2, 3, 4], columns, auto_detect_types=False)
        assert type(collection2.columns["temp"]) == Column
        assert type(collection2.columns["status"]) == Column
        assert type(collection2.columns["empty"]) == Column

    def test_column_collection_auto_detect_method(self):
        """auto_detect_column_types()メソッドのテスト"""
        # 通常のColumnで初期化
        columns = {
            "temp": Column(None, "temp", "°C", [1, 2, 3]),
            "status": Column(None, "status", "", ["OK", "Error", "OK"]),
            "empty": Column(None, "empty", "", [None, None, None]),
            "mixed": Column(None, "mixed", "", [1, "Error", 3]),
        }
        collection = ColumnCollection([1, 2, 3], columns)

        # 初期状態ではすべて標準のColumn
        assert type(collection.columns["temp"]) == Column
        assert type(collection.columns["status"]) == Column
        assert type(collection.columns["empty"]) == Column

        # 型を自動判定
        collection.auto_detect_column_types()

        # 判定後は適切な型に変換されている
        assert isinstance(collection.columns["temp"], NumberColumn)
        assert isinstance(collection.columns["status"], StringColumn)
        assert isinstance(collection.columns["empty"], InvalidColumn)
        assert type(collection.columns["mixed"]) == Column  # 混在型は変換されない

    def test_column_collection_from_file_with_auto_detect(self):
        """from_fileメソッドでの自動判定テスト（モック）"""
        # ファイルの内容をモック
        mock_content = "CH,CH,CH,CH\nTemp,Status,Empty,Mixed\n°C,,,\n1,OK,None,1\n2.5,Error,None,text\n3,OK,None,3\n"

        # ファイルのオープンをモック
        with mock.patch("builtins.open", mock.mock_open(read_data=mock_content)):
            # ファイルパスの存在チェックをモック
            with mock.patch("pathlib.Path.exists", return_value=True):
                # from_streamメソッドをモック
                with mock.patch(
                    "src.tascpy.core.collection.ColumnCollection.from_stream"
                ) as mock_from_stream:
                    # モックされたfrom_streamの戻り値を設定
                    mock_collection = ColumnCollection(
                        [1, 2, 3],
                        {
                            "Temp": Column(None, "Temp", "°C", [1, 2.5, 3]),
                            "Status": Column(None, "Status", "", ["OK", "Error", "OK"]),
                            "Empty": Column(None, "Empty", "", [None, None, None]),
                            "Mixed": Column(None, "Mixed", "", [1, "text", 3]),
                        },
                    )
                    mock_from_stream.return_value = mock_collection

                    # auto_detect_typesをTrueにして呼び出し
                    result = ColumnCollection.from_file(
                        "dummy.csv", auto_detect_types=True
                    )

                    # auto_detect_column_typesが呼ばれることを確認するのは難しいため、
                    # 代わりに自分でauto_detect_column_typesを呼び出して期待される結果と比較
                    expected = mock_collection.clone()
                    expected.auto_detect_column_types()

                    # 型の比較
                    for name, column in expected.columns.items():
                        assert type(column) == type(result.columns[name])
