import pytest
import math
import numpy as np
from tascpy.analytics.operations.core.math import (
    add,
    subtract,
    multiply,
    divide,
    evaluate,
    diff,
    integrate,
    log, sqrt, pow, abs_values, abs as math_abs, round_values, normalize,
    average_across
)
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.analytics.operations.proxy import CollectionOperations


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
    """CollectionOperationsのフィクスチャ"""
    return CollectionOperations(sample_collection)


class TestAddOperation:
    """add関数の構造テスト"""
    def test_add_columns(self, sample_collection):
        result = add(sample_collection, "A", "B")
        assert "A+B" in result.columns
        assert isinstance(result, ColumnCollection)
        assert isinstance(result["A+B"].metadata, dict)

    def test_add_constant(self, sample_collection):
        result = add(sample_collection, "A", 10)
        assert "A+10" in result.columns

class TestSubtractOperation:
    """subtract関数の構造テスト"""
    def test_subtract_columns(self, sample_collection):
        result = subtract(sample_collection, "A", "B")
        assert "A-B" in result.columns

class TestMultiplyOperation:
    """multiply関数の構造テスト"""
    def test_multiply_columns(self, sample_collection):
        result = multiply(sample_collection, "A", "B")
        assert "A*B" in result.columns

class TestDivideOperation:
    """divide関数の構造テスト"""
    def test_divide_columns(self, sample_collection):
        result = divide(sample_collection, "C", "A")
        assert "C/A" in result.columns

class TestEvaluateOperation:
    """evaluate関数の構造テスト"""
    def test_simple_expression(self, sample_collection):
        result = evaluate(sample_collection, "A + B * 2")
        assert "expression_result" in result.columns
        assert isinstance(result["expression_result"].metadata, dict)

class TestDiffOperation:
    """diff関数の構造テスト"""
    def test_diff_basic(self, sample_collection):
        result = diff(sample_collection, "A", "B")
        assert "d(A)/d(B)" in result.columns
        assert isinstance(result["d(A)/d(B)"].metadata, dict)

class TestIntegrateOperation:
    """integrate関数の構造テスト"""
    def test_integrate_constant(self, sample_collection):
        result = integrate(sample_collection, "A", "B")
        assert "∫A·dB" in result.columns
        assert isinstance(result["∫A·dB"].metadata, dict)

class TestExponentialAndLogarithmicFunctions:
    def test_log_natural(self, sample_collection):
        result = log(sample_collection, "log_input")
        assert isinstance(result, ColumnCollection)

    def test_log_base10(self, sample_collection):
        result = log(sample_collection, "log_input", base=10)
        assert isinstance(result, ColumnCollection)

    def test_log_custom_base(self, sample_collection):
        result = log(sample_collection, "log_input", base=2)
        assert isinstance(result, ColumnCollection)

    def test_log_negative(self, sample_collection):
        result = log(sample_collection, "negative")
        assert isinstance(result, ColumnCollection)

class TestPowerFunctions:
    def test_sqrt(self, sample_collection):
        result = sqrt(sample_collection, "sqrt_input")
        assert isinstance(result, ColumnCollection)

    def test_sqrt_negative(self, sample_collection):
        result = sqrt(sample_collection, "negative")
        assert isinstance(result, ColumnCollection)

    def test_pow(self, sample_collection):
        result = pow(sample_collection, "exp_input", 2)
        assert isinstance(result, ColumnCollection)

class TestOtherFunctions:
    def test_abs(self, sample_collection):
        result = abs_values(sample_collection, "abs_input")
        assert isinstance(result, ColumnCollection)

    def test_round_values(self, sample_collection):
        result0 = round_values(sample_collection, "abs_input", decimals=0)
        assert isinstance(result0, ColumnCollection)
        
    def test_with_none(self, sample_collection):
        result_abs = abs_values(sample_collection, "with_none")
        assert isinstance(result_abs, ColumnCollection)

class TestNormalizationFunctions:
    def test_normalize_minmax(self, sample_collection):
        result = normalize(sample_collection, "norm_input", method="minmax")
        assert isinstance(result, ColumnCollection)

    def test_normalize_zscore(self, sample_collection):
        result = normalize(sample_collection, "norm_input", method="zscore")
        assert isinstance(result, ColumnCollection)

    def test_normalize_constant_values(self):
        collection = ColumnCollection(
            step=[1, 2, 3, 4, 5],
            columns={"const": [10, 10, 10, 10, 10]}
        )
        result_minmax = normalize(collection, "const", method="minmax")
        assert isinstance(result_minmax, ColumnCollection)

    def test_normalize_with_none(self, sample_collection):
        result = normalize(sample_collection, "with_none", method="minmax")
        assert isinstance(result, ColumnCollection)

    def test_invalid_normalize_method(self, sample_collection):
        with pytest.raises(ValueError, match="methodは"):
            normalize(sample_collection, "norm_input", method="invalid")

class TestErrorHandling:
    def test_nonexistent_column(self, sample_collection):
        with pytest.raises(KeyError):
            abs_values(sample_collection, "nonexistent")

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

class TestAverageAcrossOperation:
    def test_average_across_basic(self, sample_collection):
        # A=[1,2,3,4,5], B=[5,4,3,2,1]
        result = average_across(sample_collection, "A", "B", result_column="avg_AB")
        assert "avg_AB" in result.columns
        np.testing.assert_allclose(result["avg_AB"].values, [3.0, 3.0, 3.0, 3.0, 3.0])

    def test_average_across_with_none(self, sample_collection):
        # A=[1,2,3,4,5], with_none=[1,None,3,None,5]
        result = average_across(sample_collection, "A", "with_none", result_column="avg_A_none")
        # Defaults to ignore_nan=True
        # Row 1: (2 + None) -> 2.0
        # Row 3: (4 + None) -> 4.0
        np.testing.assert_allclose(result["avg_A_none"].values, [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_average_across_strict_nan(self, sample_collection):
        result = average_across(sample_collection, "A", "with_none", ignore_nan=False, result_column="avg_A_none_strict")
        # Row 1 and 3 should be NaN
        vals = result["avg_A_none_strict"].values
        assert vals[0] == 1.0
        assert np.isnan(vals[1])
        assert vals[2] == 3.0
        assert np.isnan(vals[3])
        assert vals[4] == 5.0