import pytest
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.analytics.operations.proxy import CollectionOperations
from tascpy.analytics.operations.core.stats import moving_average, detect_outliers


@pytest.fixture
def sample_collection():
    return ColumnCollection(
        step=[1, 2, 3, 4, 5, 6, 7],
        columns={
            "normal": Column("1", "Normal Data", "", [10, 20, 30, 40, 50, 60, 70]),
            "with_outliers": Column("2", "Data with Outliers", "", [10, 20, 100, 40, 50, 200, 70]),
            "with_none": Column("3", "Data with None", "", [10, None, 30, None, 50, 60, None]),
        },
        metadata={"description": "Test Collection for Stats Operations"},
    )


@pytest.fixture
def ops(sample_collection):
    return CollectionOperations(sample_collection)


class TestMovingAverage:
    """moving_average関数の構造テスト"""

    def test_basic_moving_average(self, sample_collection):
        result = moving_average(sample_collection, "normal", window_size=3)
        assert isinstance(result, ColumnCollection)
        assert "ma3(normal)" in result.columns
        assert len(result["ma3(normal)"].values) == 7

    def test_custom_result_column(self, sample_collection):
        result = moving_average(
            sample_collection, "normal", window_size=5, result_column="smooth_data"
        )
        assert isinstance(result, ColumnCollection)
        assert "smooth_data" in result.columns

    def test_with_none_values(self, sample_collection):
        result = moving_average(sample_collection, "with_none", window_size=3)
        assert isinstance(result, ColumnCollection)
        assert "ma3(with_none)" in result.columns

    def test_edge_handling(self, sample_collection):
        symmetric = moving_average(
            sample_collection, "normal", window_size=3, edge_handling="symmetric"
        )
        asymmetric = moving_average(
            sample_collection, "normal", window_size=3, edge_handling="asymmetric"
        )
        assert isinstance(symmetric, ColumnCollection)
        assert isinstance(asymmetric, ColumnCollection)


class TestDetectOutliers:
    """detect_outliers関数の構造テスト"""

    def test_basic_outlier_detection(self, sample_collection):
        result = detect_outliers(
            sample_collection, "with_outliers", window_size=3, threshold=0.5
        )
        assert isinstance(result, ColumnCollection)
        assert "outlier(with_outliers)" in result.columns

    def test_custom_threshold(self, sample_collection):
        high_threshold = detect_outliers(sample_collection, "with_outliers", threshold=0.8)
        low_threshold = detect_outliers(sample_collection, "with_outliers", threshold=0.3)
        assert isinstance(high_threshold, ColumnCollection)
        assert isinstance(low_threshold, ColumnCollection)

    def test_operations_integration(self, ops):
        result = (
            ops.moving_average("normal", window_size=5)
            .detect_outliers("with_outliers", window_size=3, threshold=0.5)
            .end()
        )
        assert isinstance(result, ColumnCollection)
        assert "ma5(normal)" in result.columns
        assert "outlier(with_outliers)" in result.columns

    def test_with_none_values(self, sample_collection):
        result = detect_outliers(
            sample_collection, "with_none", window_size=3, threshold=0.5
        )
        assert isinstance(result, ColumnCollection)
        assert "outlier(with_none)" in result.columns
