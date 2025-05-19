import pytest
import math
from src.tascpy.operations.core.math import (
    add,
    subtract,
    multiply,
    divide,
    evaluate,
    diff,
    integrate
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


class TestDiffOperation:
    """diff関数のテスト"""
    
    @pytest.fixture
    def diff_collection(self):
        """微分テスト用のColumnCollectionフィクスチャ"""
        # 単位なしの基本列を作成
        collection = ColumnCollection(
            step=[1, 2, 3, 4, 5],
            columns={
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y": [1.0, 4.0, 9.0, 16.0, 25.0],  # y = x^2
                "y_linear": [2.0, 4.0, 6.0, 8.0, 10.0],  # y = 2*x
                "with_none": [1.0, None, 9.0, None, 25.0],
            },
            metadata={"description": "Test Collection for Differentiation"},
        )
        
        # 単位付き列を追加（既存の列を直接参照）
        collection.add_column("x_units", collection["x"].values)
        collection.add_column("y_units", collection["y"].values)
        
        # 単位情報を設定
        collection.columns["x_units"].unit = "m"
        collection.columns["y_units"].unit = "N"
        
        return collection

    def test_diff_basic(self, diff_collection):
        """基本的な微分機能のテスト"""
        # y = x^2 の微分は dy/dx = 2x
        result = diff(diff_collection, "y", "x")
        
        assert "d(y)/d(x)" in result.columns
        # 中心差分法の結果（端点は前方/後方差分）
        expected = [3.0, 4.0, 6.0, 8.0, 9.0]
        assert [round(v, 6) for v in result["d(y)/d(x)"].values] == [round(e, 6) for e in expected]

    def test_diff_linear(self, diff_collection):
        """線形関数の微分テスト"""
        # y = 2*x の微分は dy/dx = 2（定数）
        result = diff(diff_collection, "y_linear", "x")
        
        assert "d(y_linear)/d(x)" in result.columns
        expected = [2.0, 2.0, 2.0, 2.0, 2.0]
        assert [round(v, 6) for v in result["d(y_linear)/d(x)"].values] == [round(e, 6) for e in expected]

    def test_diff_methods(self, diff_collection):
        """各種微分メソッドのテスト"""
        # central
        central_result = diff(diff_collection, "y", "x", method="central")
        # forward
        forward_result = diff(diff_collection, "y", "x", method="forward")
        # backward
        backward_result = diff(diff_collection, "y", "x", method="backward")
        
        # 中心差分と前方差分、後方差分の結果は異なる
        assert central_result["d(y)/d(x)"].values != forward_result["d(y)/d(x)"].values
        assert central_result["d(y)/d(x)"].values != backward_result["d(y)/d(x)"].values
        
        # y = x^2 の場合：
        # forward差分: [3.0, 5.0, 7.0, 9.0, 9.0]
        # backward差分: [3.0, 3.0, 5.0, 7.0, 9.0]
        # 最後の値はforward差分では最後の値を繰り返し、backward差分では最初の値を繰り返す
        expected_forward = [3.0, 5.0, 7.0, 9.0, 9.0]
        expected_backward = [3.0, 3.0, 5.0, 7.0, 9.0]
        
        assert [round(v, 6) for v in forward_result["d(y)/d(x)"].values] == [round(e, 6) for e in expected_forward]
        assert [round(v, 6) for v in backward_result["d(y)/d(x)"].values] == [round(e, 6) for e in expected_backward]

    def test_diff_with_none(self, diff_collection):
        """None値を含む列の微分テスト"""
        result = diff(diff_collection, "with_none", "x")
        
        assert "d(with_none)/d(x)" in result.columns
        # None値を含むデータの微分では、None値の位置は結果もNone
        # [1.0, None, 9.0, None, 25.0] -> 微分結果
        expected = [None, None, None, None, None]
        assert result["d(with_none)/d(x)"].values == expected

    def test_diff_custom_result_column(self, diff_collection):
        """カスタムの結果列名を指定したテスト"""
        result_column = "derivative_result"
        result = diff(diff_collection, "y", "x", result_column=result_column)
        
        assert result_column in result.columns
        # 中心差分法の結果
        expected = [3.0, 4.0, 6.0, 8.0, 9.0]
        assert [round(v, 6) for v in result[result_column].values] == [round(e, 6) for e in expected]

    def test_diff_in_place(self, diff_collection):
        """in_place=True の場合のテスト"""
        # 元のオブジェクトを変更する
        result = diff(diff_collection, "y", "x", in_place=True)
        
        assert "d(y)/d(x)" in result.columns
        assert "d(y)/d(x)" in diff_collection.columns  # 元のオブジェクトが変更されていることを確認
        assert id(result) == id(diff_collection)  # 同じオブジェクトであることを確認

    def test_diff_invalid_method(self, diff_collection):
        """無効な微分メソッドのテスト"""
        with pytest.raises(ValueError, match="Invalid method"):
            diff(diff_collection, "y", "x", method="invalid_method")

    def test_diff_insufficient_data(self):
        """データポイントが不足している場合のテスト"""
        # 1点だけのデータ
        collection = ColumnCollection(
            step=[1],
            columns={"x": [1.0], "y": [1.0]},
        )
        with pytest.raises(ValueError, match="有効なデータポイントが不足しています"):
            diff(collection, "y", "x")

    def test_diff_nonexistent_column(self, diff_collection):
        """存在しない列を指定した場合のテスト"""
        with pytest.raises(KeyError, match="列 'nonexistent' が存在しません"):
            diff(diff_collection, "nonexistent", "x")
        
        with pytest.raises(KeyError, match="列 'nonexistent' が存在しません"):
            diff(diff_collection, "y", "nonexistent")

    def test_diff_with_units(self, diff_collection):
        """単位付き列の微分での単位伝播テスト"""
        result = diff(diff_collection, "y_units", "x_units")
        
        assert "d(y_units)/d(x_units)" in result.columns
        # 単位が正しく伝播される
        expected_unit = "N/m"
        # 単位情報が付いているかチェック
        assert hasattr(result["d(y_units)/d(x_units)"], "unit")
        assert result["d(y_units)/d(x_units)"].unit == expected_unit


class TestIntegrateOperation:
    """integrate関数のテスト"""
    
    @pytest.fixture
    def integrate_collection(self):
        """積分テスト用のColumnCollectionフィクスチャ"""
        # 単位なしの基本列を作成
        collection = ColumnCollection(
            step=[1, 2, 3, 4, 5],
            columns={
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y_const": [2.0, 2.0, 2.0, 2.0, 2.0],  # y = 2 (定数関数)
                "y_linear": [1.0, 2.0, 3.0, 4.0, 5.0],  # y = x (線形関数)
                "with_none": [1.0, None, 3.0, None, 5.0],
            },
            metadata={"description": "Test Collection for Integration"},
        )
        
        # 単位付き列を追加（既存の列を直接参照）
        collection.add_column("x_units", collection["x"].values)
        collection.add_column("y_units", collection["y_const"].values)
        
        # 単位情報を設定（直接単位プロパティを設定）
        collection.columns["x_units"].unit = "m"
        collection.columns["y_units"].unit = "N"
        
        return collection

    def test_integrate_constant(self, integrate_collection):
        """定数関数の積分テスト"""
        # ∫2 dx = 2x
        result = integrate(integrate_collection, "y_const", "x")
        
        assert "∫y_const·dx" in result.columns
        # 台形積分の結果（初期値0から）
        # 1.0 -> 0 + (1*2) = 2.0
        # 2.0 -> 2.0 + (1*2) = 4.0
        # 3.0 -> 4.0 + (1*2) = 6.0
        # 4.0 -> 6.0 + (1*2) = 8.0
        # 5.0 -> 8.0 + (1*2) = 10.0
        expected = [2.0, 4.0, 6.0, 8.0, 10.0]
        assert [round(v, 6) for v in result["∫y_const·dx"].values] == [round(e, 6) for e in expected]

    def test_integrate_linear(self, integrate_collection):
        """線形関数の積分テスト"""
        # ∫x dx = x²/2
        result = integrate(integrate_collection, "y_linear", "x")
        
        assert "∫y_linear·dx" in result.columns
        # 台形積分の結果
        # 1.0 -> 0 + (1*(1+1)/2) = 1.0
        # 2.0 -> 1.0 + (1*(1+2)/2) = 1.0 + 1.5 = 2.5
        # 3.0 -> 2.5 + (1*(2+3)/2) = 2.5 + 2.5 = 5.0
        # 4.0 -> 5.0 + (1*(3+4)/2) = 5.0 + 3.5 = 8.5
        # 5.0 -> 8.5 + (1*(4+5)/2) = 8.5 + 4.5 = 13.0
        expected = [1.0, 2.5, 5.0, 8.5, 13.0]
        assert [round(v, 6) for v in result["∫y_linear·dx"].values] == [round(e, 6) for e in expected]

    def test_integrate_with_initial_value(self, integrate_collection):
        """初期値を指定した積分テスト"""
        initial_value = 5.0
        result = integrate(integrate_collection, "y_const", "x", initial_value=initial_value)
        
        assert "∫y_const·dx" in result.columns
        # 台形積分の結果（初期値5.0から）
        expected = [5.0 + 2.0, 7.0 + 2.0, 9.0 + 2.0, 11.0 + 2.0, 13.0 + 2.0]
        assert [round(v, 6) for v in result["∫y_const·dx"].values] == [round(e, 6) for e in expected]

    def test_integrate_with_none(self, integrate_collection):
        """None値を含む列の積分テスト"""
        result = integrate(integrate_collection, "with_none", "x")
        
        assert "∫with_none·dx" in result.columns
        # None値を含むデータの積分では、None値の位置は結果もNone
        expected = [1.0, None, None, None, None]
        # 最初の値は計算可能、残りはNoneとなる
        assert result["∫with_none·dx"].values[0] == expected[0]
        assert all(v is None for v in result["∫with_none·dx"].values[1:])

    def test_integrate_custom_result_column(self, integrate_collection):
        """カスタムの結果列名を指定したテスト"""
        result_column = "integral_result"
        result = integrate(integrate_collection, "y_const", "x", result_column=result_column)
        
        assert result_column in result.columns
        # 台形積分の結果
        expected = [2.0, 4.0, 6.0, 8.0, 10.0]
        assert [round(v, 6) for v in result[result_column].values] == [round(e, 6) for e in expected]

    def test_integrate_in_place(self, integrate_collection):
        """in_place=True の場合のテスト"""
        # 元のオブジェクトを変更する
        result = integrate(integrate_collection, "y_const", "x", in_place=True)
        
        assert "∫y_const·dx" in result.columns
        assert "∫y_const·dx" in integrate_collection.columns  # 元のオブジェクトが変更されていることを確認
        assert id(result) == id(integrate_collection)  # 同じオブジェクトであることを確認

    def test_integrate_invalid_method(self, integrate_collection):
        """無効な積分メソッドのテスト"""
        with pytest.raises(ValueError, match="現在は trapezoid 積分のみサポートしています"):
            integrate(integrate_collection, "y_const", "x", method="simpson")

    def test_integrate_insufficient_data(self):
        """データポイントが不足している場合のテスト"""
        # 1点だけのデータ
        collection = ColumnCollection(
            step=[1],
            columns={"x": [1.0], "y": [1.0]},
        )
        with pytest.raises(ValueError, match="有効なデータポイントが不足しています"):
            integrate(collection, "y", "x")

    def test_integrate_nonexistent_column(self, integrate_collection):
        """存在しない列を指定した場合のテスト"""
        with pytest.raises(KeyError, match="列 'nonexistent' が存在しません"):
            integrate(integrate_collection, "nonexistent", "x")
        
        with pytest.raises(KeyError, match="列 'nonexistent' が存在しません"):
            integrate(integrate_collection, "y_const", "nonexistent")

    def test_integrate_with_units(self, integrate_collection):
        """単位付き列の積分での単位伝播テスト"""
        result = integrate(integrate_collection, "y_units", "x_units")
        
        assert "∫y_units·dx_units" in result.columns
        # 単位が正しく伝播される
        expected_unit = "N·m"
        # 単位情報が付いているかチェック
        assert hasattr(result["∫y_units·dx_units"], "unit")
        assert result["∫y_units·dx_units"].unit == expected_unit

    def test_integrate_unsorted_data(self):
        """ソートされていないデータでのテスト（積分は順序に依存する）"""
        unsorted_collection = ColumnCollection(
            step=[1, 2, 3, 4, 5],  # stepパラメータを追加
            columns={
                "x": [5.0, 1.0, 3.0, 2.0, 4.0],  # 順序がバラバラ
                "y": [2.0, 2.0, 2.0, 2.0, 2.0],  # y = 2 (定数関数)
            },
        )
        result = integrate(unsorted_collection, "y", "x")
        
        assert "∫y·dx" in result.columns
        # 順序がバラバラでも正しく積分される（内部でソート）
        # x=[1.0, 2.0, 3.0, 4.0, 5.0]の順に積分
        expected_sorted = [2.0, 4.0, 6.0, 8.0, 10.0]
        # ただし、結果の配列はもとの順序を保持（値が対応する）
        expected = [10.0, 2.0, 6.0, 4.0, 8.0]
        assert [round(v, 6) for v in result["∫y·dx"].values] == [round(e, 6) for e in expected]