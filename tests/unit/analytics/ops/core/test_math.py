import pytest
import math
import numpy as np
from collections.abc import Mapping
from tascpy.core.collection import ColumnCollection


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
            "angle_deg": [0, 30, 45, 60, 90],
            "angle_rad": [0, 0.5, 0.7, 1.0, 1.5],
            "exp_input": [-1.0, 0.0, 1.0, 2.0, 3.0],
            "log_input": [1.0, 2.0, 5.0, 10.0, 100.0],
            "sqrt_input": [0.0, 1.0, 4.0, 9.0, 16.0],
            "abs_input": [-5.0, -3.0, 0.0, 3.0, 5.0],
            "norm_input": [10, 20, 30, 40, 50],
            "negative": [-4.0, -1.0, 0.0, 1.0, 4.0],
        },
        metadata={"description": "Test Collection"},
    )

@pytest.fixture
def ops(sample_collection):
    """操作オブジェクトのフィクスチャ"""
    return sample_collection.ops


class TestAddOperation:
    """add関数の構造テスト"""
    def test_add_columns(self, sample_collection):
        result = sample_collection.ops.add("A", "B").end()
        assert "A+B" in result.columns
        assert isinstance(result, ColumnCollection)
        assert isinstance(result["A+B"].attrs, Mapping)

    def test_add_constant(self, sample_collection):
        result = sample_collection.ops.add("A", 10).end()
        assert "A+10" in result.columns

class TestSubtractOperation:
    """subtract関数の構造テスト"""
    def test_subtract_columns(self, sample_collection):
        result = sample_collection.ops.subtract("A", "B").end()
        assert "A-B" in result.columns

class TestMultiplyOperation:
    """multiply関数の構造テスト"""
    def test_multiply_columns(self, sample_collection):
        result = sample_collection.ops.multiply("A", "B").end()
        assert "A*B" in result.columns

class TestDivideOperation:
    """divide関数の構造テスト"""
    def test_divide_columns(self, sample_collection):
        result = sample_collection.ops.divide("C", "A").end()
        assert "C/A" in result.columns

class TestCalculateOperation:
    """calculate: 関数の引数名を列名として値を渡す"""

    def test_lambda(self, sample_collection):
        result = sample_collection.ops.calculate(lambda A, B: A + B * 2, result_column="C", unit="kN").end()
        a, b = sample_collection["A"].values, sample_collection["B"].values
        np.testing.assert_allclose(result["C"].values, a + b * 2)
        assert result["C"].unit == "kN"

    def test_default_names(self, sample_collection):
        def doubled(A):
            return A * 2

        assert "doubled" in sample_collection.ops.calculate(doubled).end().columns
        assert "calculate" in sample_collection.ops.calculate(lambda A: A).end().columns

    def test_missing_values_are_nan_and_scalar_broadcasts(self):
        coll = ColumnCollection({"A": [1.0, None, 3.0]})
        np.testing.assert_array_equal(coll.ops.calculate(lambda A: A * 2).end()["calculate"].values,
                                      [2.0, np.nan, 6.0])
        assert coll.ops.calculate(lambda: 5.0).end()["calculate"].to_list() == [5.0, 5.0, 5.0]

    def test_column_mapping(self):
        coll = ColumnCollection({"Force 1": [1.0, 2.0]})
        result = coll.ops.calculate(lambda f: f * 10, columns={"f": "Force 1"}, result_column="F").end()
        assert result["F"].to_list() == [10.0, 20.0]

    def test_inputs_are_not_modified(self):
        coll = ColumnCollection({"A": [1.0, 2.0]})

        def mutate(A):
            A[:] = 0
            return A

        coll.ops.calculate(mutate)
        assert coll["A"].to_list() == [1.0, 2.0]

    def test_positional_only_and_keyword_only_parameters(self):
        coll = ColumnCollection({"A": [1.0, 2.0], "B": [10.0, 20.0], "C": [100.0, 200.0]})

        def combine(A, /, B, *, C):
            return A + B + C

        assert coll.ops.calculate(combine).end()["combine"].to_list() == [111.0, 222.0]

        def first(x, /):
            return x * 2

        result = coll.ops.calculate(first, columns={"x": "B"}).end()
        assert result["first"].to_list() == [20.0, 40.0]

    def test_errors(self, sample_collection):
        with pytest.raises(KeyError, match="'X'"):
            sample_collection.ops.calculate(lambda X: X)
        with pytest.raises(ValueError, match="可変長引数"):
            sample_collection.ops.calculate(lambda *cols: cols[0])
        with pytest.raises(ValueError, match="行数"):
            sample_collection.ops.calculate(lambda A: A[:2])
        with pytest.raises(TypeError, match="数値列ではありません"):
            ColumnCollection({"S": ["x"]}).ops.calculate(lambda S: S)

class TestDiffOperation:
    """diff関数の構造テスト"""
    def test_diff_basic(self, sample_collection):
        result = sample_collection.ops.diff("A", "B").end()
        assert "d(A)/d(B)" in result.columns
        assert isinstance(result["d(A)/d(B)"].attrs, Mapping)

class TestIntegrateOperation:
    """integrate関数の構造テスト"""
    def test_integrate_constant(self, sample_collection):
        result = sample_collection.ops.integrate("A", "B").end()
        assert "∫AdB" in result.columns
        assert isinstance(result["∫AdB"].attrs, Mapping)

class TestExponentialAndLogarithmicFunctions:
    def test_log_natural(self, sample_collection):
        result = sample_collection.ops.log("log_input").end()
        assert isinstance(result, ColumnCollection)

    def test_log_base10(self, sample_collection):
        result = sample_collection.ops.log("log_input", base=10).end()
        assert isinstance(result, ColumnCollection)

    def test_log_custom_base(self, sample_collection):
        result = sample_collection.ops.log("log_input", base=2).end()
        assert isinstance(result, ColumnCollection)

    def test_log_negative(self, sample_collection):
        result = sample_collection.ops.log("negative").end()
        assert isinstance(result, ColumnCollection)

class TestPowerFunctions:
    def test_sqrt(self, sample_collection):
        result = sample_collection.ops.sqrt("sqrt_input").end()
        assert isinstance(result, ColumnCollection)

    def test_sqrt_negative(self, sample_collection):
        result = sample_collection.ops.sqrt("negative").end()
        assert isinstance(result, ColumnCollection)

    def test_pow(self, sample_collection):
        result = sample_collection.ops.pow("exp_input", 2).end()
        assert isinstance(result, ColumnCollection)

class TestOtherFunctions:
    def test_abs(self, sample_collection):
        result = sample_collection.ops.abs_values("abs_input").end()
        assert isinstance(result, ColumnCollection)

    def test_round_values(self, sample_collection):
        result0 = sample_collection.ops.round_values("abs_input", decimals=0).end()
        assert isinstance(result0, ColumnCollection)
        
    def test_with_none(self, sample_collection):
        result_abs = sample_collection.ops.abs_values("with_none").end()
        assert isinstance(result_abs, ColumnCollection)

class TestNormalizationFunctions:
    def test_normalize_minmax(self, sample_collection):
        result = sample_collection.ops.normalize("norm_input", method="minmax").end()
        assert isinstance(result, ColumnCollection)

    def test_normalize_zscore(self, sample_collection):
        result = sample_collection.ops.normalize("norm_input", method="zscore").end()
        assert isinstance(result, ColumnCollection)

    def test_normalize_constant_values(self):
        collection = ColumnCollection(
            step=[1, 2, 3, 4, 5],
            columns={"const": [10, 10, 10, 10, 10]}
        )
        result_minmax = collection.ops.normalize("const", method="minmax").end()
        assert isinstance(result_minmax, ColumnCollection)

    def test_normalize_with_none(self, sample_collection):
        result = sample_collection.ops.normalize("with_none", method="minmax").end()
        assert isinstance(result, ColumnCollection)

    def test_invalid_normalize_method(self, sample_collection):
        with pytest.raises(ValueError, match="methodは"):
            sample_collection.ops.normalize("norm_input", method="invalid").end()

class TestErrorHandling:
    def test_nonexistent_column(self, sample_collection):
        with pytest.raises(KeyError):
            sample_collection.ops.abs_values("nonexistent").end()

class TestOperationChaining:
    def test_chained_operations(self, ops):
        result = (
            ops.abs_values("negative")
            .pow("abs(negative)", 2)
            .end()
        )
        assert isinstance(result, ColumnCollection)
    
    def test_complex_transform_chain(self, ops):
        result = (
            ops.normalize("norm_input", method="minmax")
            .pow("norm_minmax(norm_input)", 2)
            .round_values("norm_minmax(norm_input)^2", 1)
            .end()
        )
        assert isinstance(result, ColumnCollection)

class TestAverageColumnsOperation:
    def test_average_columns_basic(self, sample_collection):
        # A=[1,2,3,4,5], B=[5,4,3,2,1]
        result = sample_collection.ops.average_columns(["A", "B"], result_column="avg_AB").end()
        assert "avg_AB" in result.columns
        np.testing.assert_allclose(result["avg_AB"].values, [3.0, 3.0, 3.0, 3.0, 3.0])

    def test_average_columns_with_none(self, sample_collection):
        # A=[1,2,3,4,5], with_none=[1,None,3,None,5]
        result = sample_collection.ops.average_columns(["A", "with_none"], result_column="avg_A_none").end()
        # Defaults to ignore_nan=True
        # Row 1: (2 + None) -> 2.0
        # Row 3: (4 + None) -> 4.0
        np.testing.assert_allclose(result["avg_A_none"].values, [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_average_columns_strict_nan(self, sample_collection):
        result = sample_collection.ops.average_columns(["A", "with_none"], ignore_nan=False, result_column="avg_A_none_strict").end()
        # Row 1 and 3 should be NaN
        vals = result["avg_A_none_strict"].values
        assert vals[0] == 1.0
        assert np.isnan(vals[1])
        assert vals[2] == 3.0
        assert np.isnan(vals[3])
        assert vals[4] == 5.0

class TestUnitPropagation:
    def test_units_follow_design_rules(self):
        c = ColumnCollection({"P": [1.0, 2.0], "d": [0.5, 1.0]}, units={"P": "kN", "d": "mm"})
        r = (c.ops.add("P", "P").multiply("P", 2).multiply("P", "d").divide("P", 2, result_column="half")
             .pow("P", 2).normalize("P").diff("P", "d").calculate(lambda P: P * 2).end())
        assert r["P+P"].unit == "kN"
        assert r["P*2"].unit == "kN"
        assert r["P*d"].unit is None
        assert r["half"].unit == "kN"
        assert r["P^2"].unit is None
        assert r["norm_minmax(P)"].unit == ""
        assert r["d(P)/d(d)"].unit == "kN/mm"
        assert r["calculate"].unit is None

    def test_explicit_unit_wins(self):
        c = ColumnCollection({"P": [1.0, 2.0], "d": [0.5, 1.0]}, units={"P": "kN", "d": "mm"})
        assert c.ops.multiply("P", "d", unit="kN·mm").end()["P*d"].unit == "kN·mm"
