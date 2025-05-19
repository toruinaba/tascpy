import pytest
import math
import builtins # ビルトイン関数をインポート
from src.tascpy.operations.core.transform import (
    sin,
    cos,
    tan,
    exp,
    log,
    sqrt,
    pow,
    abs_values, # abs_values関数を直接インポート
    abs, # エイリアス名も残す
    round_values,
    normalize
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
            "angle_deg": [0, 30, 45, 60, 90],  # 度単位の角度
            "angle_rad": [0, math.pi/6, math.pi/4, math.pi/3, math.pi/2],  # ラジアン単位の角度
            "exp_input": [-1.0, 0.0, 1.0, 2.0, 3.0],  # 指数関数入力
            "log_input": [1.0, 2.0, 5.0, 10.0, 100.0],  # 対数関数入力
            "sqrt_input": [0.0, 1.0, 4.0, 9.0, 16.0],  # 平方根入力
            "abs_input": [-5.0, -3.0, 0.0, 3.0, 5.0],  # 絶対値入力
            "norm_input": [10, 20, 30, 40, 50],  # 正規化入力
            "with_none": [1.0, None, 3.0, None, 5.0],  # None値を含む
            "negative": [-4.0, -1.0, 0.0, 1.0, 4.0],  # 負の値を含む
        },
        metadata={"description": "Test Collection"},
    )


@pytest.fixture
def ops(sample_collection):
    """CollectionOperationsのフィクスチャ"""
    return CollectionOperations(sample_collection)


@pytest.fixture
def epsilon():
    """浮動小数点比較のための許容誤差"""
    return 1e-10


class TestTrigonometricFunctions:
    """三角関数のテスト"""

    def test_sin_radians(self, sample_collection, epsilon):
        """sin関数テスト（ラジアン）"""
        result = sin(sample_collection, "angle_rad")
        
        assert "sin(angle_rad)" in result.columns
        expected = [0.0, 0.5, 1/math.sqrt(2), math.sqrt(3)/2, 1.0]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["sin(angle_rad)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_sin_degrees(self, sample_collection, epsilon):
        """sin関数テスト（度）"""
        result = sin(sample_collection, "angle_deg", degrees=True)
        
        assert "sin(angle_deg)" in result.columns
        expected = [0.0, 0.5, 1/math.sqrt(2), math.sqrt(3)/2, 1.0]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["sin(angle_deg)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_cos_radians(self, sample_collection, epsilon):
        """cos関数テスト（ラジアン）"""
        result = cos(sample_collection, "angle_rad")
        
        assert "cos(angle_rad)" in result.columns
        expected = [1.0, math.sqrt(3)/2, 1/math.sqrt(2), 0.5, 0.0]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["cos(angle_rad)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_cos_degrees(self, sample_collection, epsilon):
        """cos関数テスト（度）"""
        result = cos(sample_collection, "angle_deg", degrees=True)
        
        assert "cos(angle_deg)" in result.columns
        expected = [1.0, math.sqrt(3)/2, 1/math.sqrt(2), 0.5, 0.0]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["cos(angle_deg)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_tan_radians(self, sample_collection, epsilon):
        """tan関数テスト（ラジアン）"""
        result = tan(sample_collection, "angle_rad")
        
        assert "tan(angle_rad)" in result.columns
        # 理論値 [0.0, 1/sqrt(3), 1.0, sqrt(3), inf]
        # tan(π/2)は無限大になるが、実際の計算では非常に大きな値になる
        expected = [0.0, 1/math.sqrt(3), 1.0, math.sqrt(3)]
        
        # 最初の4つの要素を比較
        for i, (actual, expected_val) in enumerate(zip(result["tan(angle_rad)"].values[:4], expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"
        
        # 5番目の要素は非常に大きな値または無限大になるはず
        assert result["tan(angle_rad)"].values[4] > 1e10 or math.isinf(result["tan(angle_rad)"].values[4])

    def test_trig_with_none(self, sample_collection):
        """None値を含む列への三角関数適用テスト"""
        result = sin(sample_collection, "with_none")
        
        assert "sin(with_none)" in result.columns
        expected = [math.sin(1.0), None, math.sin(3.0), None, math.sin(5.0)]
        
        for i in range(5):
            if expected[i] is None:
                assert result["sin(with_none)"].values[i] is None
            else:
                assert builtins.abs(result["sin(with_none)"].values[i] - expected[i]) < 1e-10


class TestExponentialAndLogarithmicFunctions:
    """指数関数と対数関数のテスト"""

    def test_exp(self, sample_collection, epsilon):
        """exp関数テスト"""
        result = exp(sample_collection, "exp_input")
        
        assert "exp(exp_input)" in result.columns
        expected = [math.exp(-1), math.exp(0), math.exp(1), math.exp(2), math.exp(3)]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["exp(exp_input)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_log_natural(self, sample_collection, epsilon):
        """自然対数のテスト"""
        result = log(sample_collection, "log_input")
        
        assert "log(log_input)" in result.columns
        expected = [math.log(1), math.log(2), math.log(5), math.log(10), math.log(100)]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["log(log_input)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_log_base10(self, sample_collection, epsilon):
        """底10の対数のテスト"""
        result = log(sample_collection, "log_input", base=10)
        
        assert "log10(log_input)" in result.columns
        expected = [0, math.log10(2), math.log10(5), 1, 2]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["log10(log_input)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_log_custom_base(self, sample_collection, epsilon):
        """カスタム底の対数のテスト"""
        base = 2
        result = log(sample_collection, "log_input", base=base)
        
        assert f"log{base}(log_input)" in result.columns
        expected = [0, 1, math.log(5, 2), math.log(10, 2), math.log(100, 2)]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result[f"log{base}(log_input)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_log_negative(self, sample_collection):
        """負の値の対数（None扱い）のテスト"""
        result = log(sample_collection, "negative")
        
        assert "log(negative)" in result.columns
        # 負の値とゼロの対数はNoneになる
        expected = [None, None, None, 0, math.log(4)]
        
        for i in range(5):
            if expected[i] is None:
                assert result["log(negative)"].values[i] is None
            else:
                assert builtins.abs(result["log(negative)"].values[i] - expected[i]) < 1e-10


class TestPowerFunctions:
    """べき乗関数のテスト"""

    def test_sqrt(self, sample_collection):
        """平方根のテスト"""
        result = sqrt(sample_collection, "sqrt_input")
        
        assert "sqrt(sqrt_input)" in result.columns
        expected = [0.0, 1.0, 2.0, 3.0, 4.0]
        assert result["sqrt(sqrt_input)"].values == expected

    def test_sqrt_negative(self, sample_collection):
        """負の値の平方根（None扱い）のテスト"""
        result = sqrt(sample_collection, "negative")
        
        assert "sqrt(negative)" in result.columns
        # 負の値の平方根はNoneになる
        expected = [None, None, 0.0, 1.0, 2.0]
        assert result["sqrt(negative)"].values == expected

    def test_pow(self, sample_collection):
        """べき乗のテスト"""
        exponent = 2
        result = pow(sample_collection, "exp_input", exponent)
        
        assert f"exp_input^{exponent}" in result.columns
        expected = [1.0, 0.0, 1.0, 4.0, 9.0]  # (-1)^2, 0^2, 1^2, 2^2, 3^2
        assert result[f"exp_input^{exponent}"].values == expected


class TestOtherFunctions:
    """その他の関数のテスト"""

    def test_abs(self, sample_collection):
        """絶対値のテスト"""
        result = abs_values(sample_collection, "abs_input")
        
        assert "abs(abs_input)" in result.columns
        expected = [5.0, 3.0, 0.0, 3.0, 5.0]
        assert result["abs(abs_input)"].values == expected

    def test_round_values(self):
        """丸め処理のテスト"""
        # Pi値の小数点以下を丸める
        collection = ColumnCollection(
            step=[1, 2, 3, 4, 5],
            columns={"pi": [3.14159, 3.14159, 3.14159, 3.14159, 3.14159]}
        )
        
        # 小数点以下0桁（整数に丸め）
        result0 = round_values(collection, "pi", decimals=0)
        assert "round(pi, 0)" in result0.columns
        expected0 = [3.0, 3.0, 3.0, 3.0, 3.0]
        assert result0["round(pi, 0)"].values == expected0
        
        # 小数点以下2桁
        result2 = round_values(collection, "pi", decimals=2)
        assert "round(pi, 2)" in result2.columns
        expected2 = [3.14, 3.14, 3.14, 3.14, 3.14]
        assert result2["round(pi, 2)"].values == expected2

    def test_with_none(self, sample_collection):
        """None値を含む列に各変換関数を適用するテスト"""
        # abs関数
        result_abs = abs_values(sample_collection, "with_none")
        assert "abs(with_none)" in result_abs.columns
        expected_abs = [1.0, None, 3.0, None, 5.0]
        assert result_abs["abs(with_none)"].values == expected_abs
        
        # round関数
        result_round = round_values(sample_collection, "with_none", decimals=1)
        assert "round(with_none, 1)" in result_round.columns
        expected_round = [1.0, None, 3.0, None, 5.0]
        assert result_round["round(with_none, 1)"].values == expected_round


class TestNormalizationFunctions:
    """正規化関数のテスト"""

    def test_normalize_minmax(self, sample_collection, epsilon):
        """Min-Max正規化のテスト"""
        result = normalize(sample_collection, "norm_input", method="minmax")
        
        assert "norm_minmax(norm_input)" in result.columns
        expected = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["norm_minmax(norm_input)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_normalize_zscore(self, sample_collection, epsilon):
        """Z-score正規化のテスト"""
        result = normalize(sample_collection, "norm_input", method="zscore")
        
        assert "norm_zscore(norm_input)" in result.columns
        
        # 平均と標準偏差を計算
        norm_values = sample_collection["norm_input"].values
        mean = sum(norm_values) / len(norm_values)
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in norm_values) / len(norm_values))
        
        # 期待値を計算
        expected = [(x - mean) / std_dev for x in norm_values]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["norm_zscore(norm_input)"].values, expected)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_normalize_constant_values(self, epsilon):
        """一定値の正規化テスト"""
        # 全て同じ値を持つ列
        collection = ColumnCollection(
            step=[1, 2, 3, 4, 5],
            columns={"const": [10, 10, 10, 10, 10]}
        )
        
        # Min-Maxの場合は0.5に
        result_minmax = normalize(collection, "const", method="minmax")
        assert "norm_minmax(const)" in result_minmax.columns
        expected_minmax = [0.5, 0.5, 0.5, 0.5, 0.5]
        
        for i, (actual, expected_val) in enumerate(zip(result_minmax["norm_minmax(const)"].values, expected_minmax)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"
        
        # Z-scoreの場合は0に
        result_zscore = normalize(collection, "const", method="zscore")
        assert "norm_zscore(const)" in result_zscore.columns
        expected_zscore = [0.0, 0.0, 0.0, 0.0, 0.0]
        
        for i, (actual, expected_val) in enumerate(zip(result_zscore["norm_zscore(const)"].values, expected_zscore)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"

    def test_normalize_with_none(self, sample_collection, epsilon):
        """None値を含む列の正規化テスト"""
        result = normalize(sample_collection, "with_none", method="minmax")
        
        assert "norm_minmax(with_none)" in result.columns
        # None値を除いて[1.0, 3.0, 5.0]を正規化すると[0.0, 0.5, 1.0]になる
        expected = [0.0, None, 0.5, None, 1.0]
        
        for i in range(5):
            if expected[i] is None:
                assert result["norm_minmax(with_none)"].values[i] is None
            else:
                assert builtins.abs(result["norm_minmax(with_none)"].values[i] - expected[i]) < epsilon

    def test_invalid_normalize_method(self, sample_collection):
        """不正な正規化方法を指定した場合のテスト"""
        with pytest.raises(ValueError, match="methodは"):
            normalize(sample_collection, "norm_input", method="invalid")


class TestErrorHandling:
    """エラー処理のテスト"""

    def test_nonexistent_column(self, sample_collection):
        """存在しない列名を指定した場合のテスト"""
        with pytest.raises(KeyError, match="列 'nonexistent' が存在しません"):
            sin(sample_collection, "nonexistent")
        
        with pytest.raises(KeyError, match="列 'nonexistent' が存在しません"):
            exp(sample_collection, "nonexistent")


class TestOperationChaining:
    """操作チェーンのテスト"""

    def test_chained_operations(self, ops, epsilon):
        """操作チェーンのテスト"""
        # angle_deg(度) -> ラジアン変換して正弦 -> 絶対値
        result = (
            ops.sin("angle_deg", degrees=True)
            .abs("sin(angle_deg)")
            .end()
        )
        
        assert "sin(angle_deg)" in result.columns
        assert "abs(sin(angle_deg))" in result.columns
        
        expected_sin = [0.0, 0.5, 1/math.sqrt(2), math.sqrt(3)/2, 1.0]
        expected_abs = expected_sin  # すべて正の値なので同じ
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["sin(angle_deg)"].values, expected_sin)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"
        
        for i, (actual, expected_val) in enumerate(zip(result["abs(sin(angle_deg))"].values, expected_abs)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"
    
    def test_complex_transform_chain(self, ops, epsilon):
        """複雑な変換チェーンのテスト"""
        # 正規化 -> 2乗 -> コサイン
        result = (
            ops.normalize("norm_input", method="minmax")
            .pow("norm_minmax(norm_input)", 2)
            .cos("norm_minmax(norm_input)^2")
            .end()
        )
        
        assert "norm_minmax(norm_input)" in result.columns
        assert "norm_minmax(norm_input)^2" in result.columns
        assert "cos(norm_minmax(norm_input)^2)" in result.columns
        
        # 正規化 [0.0, 0.25, 0.5, 0.75, 1.0]
        # 2乗 [0.0, 0.0625, 0.25, 0.5625, 1.0]
        # コサイン [1.0, 0.9980..., 0.9689..., 0.8458..., 0.5403...]
        expected_norm = [0.0, 0.25, 0.5, 0.75, 1.0]
        expected_pow = [0.0, 0.0625, 0.25, 0.5625, 1.0]
        expected_cos = [math.cos(x) for x in expected_pow]
        
        # 浮動小数点の比較は許容誤差を考慮
        for i, (actual, expected_val) in enumerate(zip(result["norm_minmax(norm_input)^2"].values, expected_pow)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"
        
        for i, (actual, expected_val) in enumerate(zip(result["cos(norm_minmax(norm_input)^2)"].values, expected_cos)):
            assert builtins.abs(actual - expected_val) < epsilon, f"Index {i}: {actual} != {expected_val}"