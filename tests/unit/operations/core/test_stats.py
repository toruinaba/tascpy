"""
統計処理操作のテスト。
移動平均と異常値検出のテストケースを含みます。
"""

import pytest
import math
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column
from src.tascpy.operations.proxy import CollectionOperations
from src.tascpy.operations.core.stats import moving_average, detect_outliers


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5, 6, 7],
        columns={
            "normal": Column("1", "Normal Data", "", [10, 20, 30, 40, 50, 60, 70]),
            "with_outliers": Column(
                "2", "Data with Outliers", "", [10, 20, 100, 40, 50, 200, 70]
            ),
            "with_none": Column(
                "3", "Data with None", "", [10, None, 30, None, 50, 60, None]
            ),
        },
        metadata={"description": "Test Collection for Stats Operations"},
    )


@pytest.fixture
def ops(sample_collection):
    """CollectionOperationsのフィクスチャ"""
    return CollectionOperations(sample_collection)


class TestMovingAverage:
    """moving_average関数のテスト"""

    def test_basic_moving_average(self, sample_collection):
        """基本的な移動平均計算のテスト"""
        result = moving_average(sample_collection, "normal", window_size=3)

        # 結果のコレクションに新しい列が追加されていることを確認
        assert "ma3(normal)" in result.columns

        # 移動平均の計算結果を検証
        expected = [15.0, 20.0, 30.0, 40.0, 50.0, 60.0, 65.0]
        assert len(result["ma3(normal)"].values) == 7

        for actual, exp in zip(result["ma3(normal)"].values, expected):
            assert abs(actual - exp) < 1e-6

    def test_custom_result_column(self, sample_collection):
        """カスタム結果列名のテスト"""
        result = moving_average(
            sample_collection, "normal", window_size=5, result_column="smooth_data"
        )

        assert "smooth_data" in result.columns
        assert len(result["smooth_data"].values) == 7

    def test_with_none_values(self, sample_collection):
        """None値を含むデータの処理テスト"""
        result = moving_average(sample_collection, "with_none", window_size=3)

        # None値を含む場合でも計算できることを確認
        assert result["ma3(with_none)"].values[1] is not None
        assert result["ma3(with_none)"].values[3] is not None

    def test_edge_handling(self, sample_collection):
        """エッジ処理オプションのテスト"""
        # symmetric エッジ処理
        symmetric = moving_average(
            sample_collection, "normal", window_size=3, edge_handling="symmetric"
        )

        # asymmetric エッジ処理（デフォルト）
        asymmetric = moving_average(
            sample_collection, "normal", window_size=3, edge_handling="asymmetric"
        )

        # エッジでの計算方法が異なることを確認
        assert symmetric["ma3(normal)"].values[0] == asymmetric["ma3(normal)"].values[0]
        assert (
            symmetric["ma3(normal)"].values[-1] == asymmetric["ma3(normal)"].values[-1]
        )


class TestDetectOutliers:
    """detect_outliers関数のテスト"""

    def test_basic_outlier_detection(self, sample_collection):
        """基本的な異常値検出のテスト"""
        result = detect_outliers(
            sample_collection, "with_outliers", window_size=3, threshold=0.5
        )

        # 結果のコレクションに新しい列が追加されていることを確認
        assert "outlier(with_outliers)" in result.columns

        # 異常値フラグを検証
        expected = [0, 0, 1, 0, 0, 1, 0]  # インデックス2と5が異常値
        assert result["outlier(with_outliers)"].values == expected

    def test_custom_threshold(self, sample_collection):
        """カスタム閾値を使用した異常値検出のテスト"""
        # 閾値を高くすると異常値が少なくなる
        high_threshold = detect_outliers(
            sample_collection, "with_outliers", threshold=0.8
        )
        # 閾値を低くすると異常値が多くなる
        low_threshold = detect_outliers(
            sample_collection, "with_outliers", threshold=0.3
        )

        high_count = sum(high_threshold["outlier(with_outliers)"].values)
        low_count = sum(low_threshold["outlier(with_outliers)"].values)

        assert high_count <= low_count

    def test_operations_integration(self, ops):
        """CollectionOperationsとの統合テスト"""
        # 操作のチェーンを使ったテスト
        result = (
            ops.moving_average("normal", window_size=5)
            .detect_outliers("with_outliers", window_size=3, threshold=0.5)
            .end()
        )

        assert "ma5(normal)" in result.columns
        assert "outlier(with_outliers)" in result.columns

    def test_with_none_values(self, sample_collection):
        """None値を含むデータの処理テスト"""
        result = detect_outliers(
            sample_collection, "with_none", window_size=3, threshold=0.5
        )

        # None値を含む場合でも計算できることを確認
        assert "outlier(with_none)" in result.columns
        assert len(result["outlier(with_none)"].values) == len(sample_collection)
