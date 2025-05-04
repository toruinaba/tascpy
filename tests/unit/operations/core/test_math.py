import pytest
import math
from src.tascpy.operations.core.math import (
    add,
    subtract,
    multiply,
    divide,
    evaluate
)
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column
from src.tascpy.operations.proxy import CollectionOperations


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "A": [1.0, 2.0, 3.0, 4.0, 5.0],
            "B": [5.0, 4.0, 3.0, 2.0, 1.0],
            "C": [10.0, 20.0, 30.0, 40.0, 50.0],
            "with_none": [1.0, None, 3.0, None, 5.0],
        },
        metadata={"description": "Test Collection"},
    )


@pytest.fixture
def ops(sample_collection):
    """CollectionOperationsのフィクスチャ"""
    return CollectionOperations(sample_collection)


class TestAddOperation:
    """add関数のテスト"""

    def test_add_columns(self, sample_collection):
        """列同士の加算テスト"""
        # A + B = [6.0, 6.0, 6.0, 6.0, 6.0]
        result = add(sample_collection, "A", "B")
        
        assert "A+B" in result.columns
        expected = [6.0, 6.0, 6.0, 6.0, 6.0]
        assert result["A+B"].values == expected

    def test_add_constant(self, sample_collection):
        """定数との加算テスト"""
        # A + 10 = [11.0, 12.0, 13.0, 14.0, 15.0]
        result = add(sample_collection, "A", 10)
        
        assert "A+10" in result.columns
        expected = [11.0, 12.0, 13.0, 14.0, 15.0]
        assert result["A+10"].values == expected

    def test_add_with_none(self, sample_collection):
        """None値を含む列の加算テスト"""
        # with_none + 5 = [6.0, None, 8.0, None, 10.0]
        result = add(sample_collection, "with_none", 5)
        
        assert "with_none+5" in result.columns
        expected = [6.0, None, 8.0, None, 10.0]
        assert result["with_none+5"].values == expected
        
        # with_none + B = [6.0, None, 6.0, None, 6.0]
        result = add(sample_collection, "with_none", "B")
        
        assert "with_none+B" in result.columns
        expected = [6.0, None, 6.0, None, 6.0]
        assert result["with_none+B"].values == expected

    def test_add_with_custom_result_column(self, sample_collection):
        """カスタムの結果列名を指定したテスト"""
        result_column = "sum_result"
        result = add(sample_collection, "A", "B", result_column=result_column)
        
        assert result_column in result.columns
        expected = [6.0, 6.0, 6.0, 6.0, 6.0]
        assert result[result_column].values == expected

    def test_add_in_place(self, sample_collection):
        """in_place=True の場合のテスト"""
        # 元のオブジェクトを変更する
        result = add(sample_collection, "A", 1, in_place=True)
        
        assert "A+1" in result.columns
        assert "A+1" in sample_collection.columns  # 元のオブジェクトが変更されていることを確認
        assert id(result) == id(sample_collection)  # 同じオブジェクトであることを確認

    def test_add_nonexistent_column(self, sample_collection):
        """存在しない列を指定した場合のテスト"""
        with pytest.raises(KeyError, match="列 'nonexistent' が存在しません"):
            add(sample_collection, "nonexistent", "B")
        
        with pytest.raises(KeyError, match="列 'nonexistent' が存在しません"):
            add(sample_collection, "A", "nonexistent")


class TestSubtractOperation:
    """subtract関数のテスト"""

    def test_subtract_columns(self, sample_collection):
        """列同士の減算テスト"""
        # A - B = [-4.0, -2.0, 0.0, 2.0, 4.0]
        result = subtract(sample_collection, "A", "B")
        
        assert "A-B" in result.columns
        expected = [-4.0, -2.0, 0.0, 2.0, 4.0]
        assert result["A-B"].values == expected

    def test_subtract_constant(self, sample_collection):
        """定数との減算テスト"""
        # A - 1 = [0.0, 1.0, 2.0, 3.0, 4.0]
        result = subtract(sample_collection, "A", 1)
        
        assert "A-1" in result.columns
        expected = [0.0, 1.0, 2.0, 3.0, 4.0]
        assert result["A-1"].values == expected

    def test_subtract_with_none(self, sample_collection):
        """None値を含む列の減算テスト"""
        # with_none - 1 = [0.0, None, 2.0, None, 4.0]
        result = subtract(sample_collection, "with_none", 1)
        
        assert "with_none-1" in result.columns
        expected = [0.0, None, 2.0, None, 4.0]
        assert result["with_none-1"].values == expected


class TestMultiplyOperation:
    """multiply関数のテスト"""

    def test_multiply_columns(self, sample_collection):
        """列同士の乗算テスト"""
        # A * B = [5.0, 8.0, 9.0, 8.0, 5.0]
        result = multiply(sample_collection, "A", "B")
        
        assert "A*B" in result.columns
        expected = [5.0, 8.0, 9.0, 8.0, 5.0]
        assert result["A*B"].values == expected

    def test_multiply_constant(self, sample_collection):
        """定数との乗算テスト"""
        # A * 2 = [2.0, 4.0, 6.0, 8.0, 10.0]
        result = multiply(sample_collection, "A", 2)
        
        assert "A*2" in result.columns
        expected = [2.0, 4.0, 6.0, 8.0, 10.0]
        assert result["A*2"].values == expected

    def test_multiply_with_none(self, sample_collection):
        """None値を含む列の乗算テスト"""
        # with_none * 2 = [2.0, None, 6.0, None, 10.0]
        result = multiply(sample_collection, "with_none", 2)
        
        assert "with_none*2" in result.columns
        expected = [2.0, None, 6.0, None, 10.0]
        assert result["with_none*2"].values == expected


class TestDivideOperation:
    """divide関数のテスト"""

    def test_divide_columns(self, sample_collection):
        """列同士の除算テスト"""
        # C / A = [10.0, 10.0, 10.0, 10.0, 10.0]
        result = divide(sample_collection, "C", "A")
        
        assert "C/A" in result.columns
        expected = [10.0, 10.0, 10.0, 10.0, 10.0]
        assert result["C/A"].values == expected

    def test_divide_constant(self, sample_collection):
        """定数との除算テスト"""
        # C / 10 = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = divide(sample_collection, "C", 10)
        
        assert "C/10" in result.columns
        expected = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert result["C/10"].values == expected

    def test_zero_division_error(self, sample_collection):
        """ゼロ除算のエラー処理テスト"""
        # エラーモード
        with pytest.raises(ValueError, match="ゼロによる除算が発生しました"):
            divide(sample_collection, "A", 0, handle_zero_division="error")
        
        # Noneモード
        result = divide(sample_collection, "A", 0, handle_zero_division="none")
        assert "A/0" in result.columns
        assert all(v is None for v in result["A/0"].values)
        
        # infモード
        result = divide(sample_collection, "A", 0, handle_zero_division="inf")
        assert "A/0" in result.columns
        for val in result["A/0"].values:
            assert math.isinf(val)

    def test_invalid_zero_division_handler(self, sample_collection):
        """不正なゼロ除算ハンドラーを指定した場合のテスト"""
        with pytest.raises(ValueError, match="handle_zero_divisionは"):
            divide(sample_collection, "A", 0, handle_zero_division="invalid")


class TestOperationChaining:
    """CollectionOperationsを使用した演算チェーンのテスト"""

    def test_chained_operations(self, ops):
        """演算のチェーンテスト"""
        # (A + 2) * 3 = [9.0, 12.0, 15.0, 18.0, 21.0]
        result = ops.add("A", 2).multiply("A+2", 3).end()
        
        assert "A+2" in result.columns
        assert "(A+2)*3" in result.columns
        
        expected_intermediate = [3.0, 4.0, 5.0, 6.0, 7.0]  # A+2
        expected_final = [9.0, 12.0, 15.0, 18.0, 21.0]     # (A+2)*3
        
        assert result["A+2"].values == expected_intermediate
        assert result["(A+2)*3"].values == expected_final


class TestEvaluateOperation:
    """evaluate関数のテスト"""

    def test_simple_expression(self, sample_collection):
        """単純な式の評価テスト"""
        # A + B * 2
        result = evaluate(sample_collection, "A + B * 2")
        
        # 結果の列名が"expression_result_{n}"という形式であることを確認
        result_column = [col for col in result.columns if col.startswith("expression_result_")][0]
        assert result_column in result.columns
        expected = [11.0, 10.0, 9.0, 8.0, 7.0]  # A + B*2 = 1+5*2, 2+4*2, ...
        assert result[result_column].values == expected

    def test_complex_expression(self, sample_collection):
        """複雑な式の評価テスト"""
        # (A + B) * (C / 10)
        result = evaluate(sample_collection, "(A + B) * (C / 10)")
        
        # 結果の列名が"expression_result_{n}"という形式であることを確認
        result_column = [col for col in result.columns if col.startswith("expression_result_")][0]
        assert result_column in result.columns
        # (1+5)*1, (2+4)*2, (3+3)*3, (4+2)*4, (5+1)*5
        expected = [6.0, 12.0, 18.0, 24.0, 30.0]
        assert result[result_column].values == expected

    def test_math_functions(self, sample_collection):
        """数学関数を含む式のテスト"""
        # sin(A) + cos(B)
        result = evaluate(sample_collection, "sin(A) + cos(B)")
        
        # 結果の列名が"expression_result_{n}"という形式であることを確認
        result_column = [col for col in result.columns if col.startswith("expression_result_")][0]
        assert result_column in result.columns
        expected = [
            math.sin(1.0) + math.cos(5.0),
            math.sin(2.0) + math.cos(4.0),
            math.sin(3.0) + math.cos(3.0),
            math.sin(4.0) + math.cos(2.0),
            math.sin(5.0) + math.cos(1.0)
        ]
        # 浮動小数点数の比較には丸めを使用
        assert [round(a, 10) for a in result[result_column].values] == [round(e, 10) for e in expected]

    def test_with_none_values(self, sample_collection):
        """None値を含む列を使用した式のテスト"""
        # with_none * 2 + A
        result = evaluate(sample_collection, "with_none * 2 + A")
        
        # 結果の列名が"expression_result_{n}"という形式であることを確認
        result_column = [col for col in result.columns if col.startswith("expression_result_")][0]
        assert result_column in result.columns
        # (1*2+1), (None), (3*2+3), (None), (5*2+5)
        expected = [3.0, None, 9.0, None, 15.0]
        assert result[result_column].values == expected

    def test_custom_result_column(self, sample_collection):
        """カスタムの結果列名を指定したテスト"""
        # A * B
        result_column = "product"
        result = evaluate(sample_collection, "A * B", result_column=result_column)
        
        assert result_column in result.columns
        expected = [5.0, 8.0, 9.0, 8.0, 5.0]
        assert result[result_column].values == expected

    def test_in_place(self, sample_collection):
        """in_place=True の場合のテスト"""
        # 元のオブジェクトを変更する
        result = evaluate(sample_collection, "A + B", result_column="sum_result", in_place=True)
        
        assert "sum_result" in result.columns
        assert "sum_result" in sample_collection.columns  # 元のオブジェクトが変更されていることを確認
        assert id(result) == id(sample_collection)  # 同じオブジェクトであることを確認

    def test_invalid_expression(self, sample_collection):
        """不正な式のテスト"""
        # 構文エラー
        with pytest.raises(ValueError, match="式の構文エラー"):
            evaluate(sample_collection, "A + * B")
        
        # 存在しないカラム
        with pytest.raises(KeyError, match="式に存在しないカラム名が含まれています"):
            evaluate(sample_collection, "A + nonexistent")
        
        # 安全でない関数呼び出し
        with pytest.raises(ValueError, match="許可されていない関数が使用されています"):
            evaluate(sample_collection, "exec(A)")
        
        # 属性アクセス
        with pytest.raises(ValueError, match="式に安全でない属性アクセスが含まれています"):
            evaluate(sample_collection, "A.__class__")