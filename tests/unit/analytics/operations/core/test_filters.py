import pytest
from tascpy.analytics.operations.core.filters import (
    filter_by_value,
    filter_out_none,
    remove_consecutive_duplicates_across,
    remove_outliers,
    search_by_value,
    search_by_range,
    search_by_step_range,
    search_by_condition,
    search_missing_values,
    search_top_n,
)
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "A": Column("1", "Column A", "N", [1, 2, 3, 4, 5]),
            "B": Column("2", "Column B", "kg", [10, 20, 30, 40, 50]),
            "C": Column("3", "Column C", "m", [100, None, 300, None, 500]),
        },
        metadata={"description": "Test Collection"},
    )


class TestFilterByValue:
    """filter_by_value関数の構造テスト"""

    def test_exact_match(self, sample_collection):
        result = filter_by_value(sample_collection, "A", 3)
        assert isinstance(result, ColumnCollection)
        assert "A" in result.columns
        assert result.metadata == sample_collection.metadata

    def test_tolerance_filter(self, sample_collection):
        result = filter_by_value(sample_collection, "A", 3, tolerance=1.0)
        assert isinstance(result, ColumnCollection)

    def test_no_match(self, sample_collection):
        result = filter_by_value(sample_collection, "A", 100)
        assert isinstance(result, ColumnCollection)

    def test_invalid_column(self, sample_collection):
        with pytest.raises(KeyError, match="列 '不存在' が存在しません"):
            filter_by_value(sample_collection, "不存在", 1)


class TestFilterOutNone:
    """filter_out_none関数の構造テスト"""

    def test_filter_all_columns_any_mode(self, sample_collection):
        result = filter_out_none(sample_collection)
        assert isinstance(result, ColumnCollection)

    def test_filter_specific_columns(self, sample_collection):
        result = filter_out_none(sample_collection, columns=["C"])
        assert isinstance(result, ColumnCollection)
        assert "A" in result.columns

    def test_filter_all_mode(self, sample_collection):
        extended_collection = ColumnCollection(
            step=[1, 2, 3, 4, 5, 6],
            columns={
                "A": Column("1", "Column A", "N", [1, 2, None, 4, 5, None]),
                "B": Column("2", "Column B", "kg", [10, None, None, 40, 50, None]),
                "C": Column("3", "Column C", "m", [100, None, 300, None, 500, None]),
            },
            metadata=sample_collection.metadata,
        )
        result = filter_out_none(extended_collection, mode="all")
        assert isinstance(result, ColumnCollection)

    def test_invalid_column(self, sample_collection):
        with pytest.raises(KeyError, match="列 '不存在' が存在しません"):
            filter_out_none(sample_collection, columns=["A", "不存在"])

    def test_invalid_mode(self, sample_collection):
        with pytest.raises(ValueError, match="モードは'any'または'all'のいずれかである必要があります"):
            filter_out_none(sample_collection, mode="invalid")

    def test_metadata_preserved(self, sample_collection):
        result = filter_out_none(sample_collection)
        assert result.metadata == sample_collection.metadata


class TestRemoveConsecutiveDuplicatesAcross:
    """remove_consecutive_duplicates_across関数の構造テスト"""

    @pytest.fixture
    def duplicate_collection(self):
        return ColumnCollection(
            step=[1, 2, 3, 4, 5, 6, 7, 8],
            columns={
                "A": Column("1", "Column A", "N", [1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0]),
                "B": Column("2", "Column B", "kg", [10.0, 20.0, 30.0, 30.0, 40.0, 50.0, 60.0, 60.0]),
                "C": Column("3", "Column C", "m", [5, 5, 2, 2, 8, 8, 9, 10]),
            },
            metadata={"description": "Test Collection with Duplicates"},
        )

    def test_all_mode(self, duplicate_collection):
        result = remove_consecutive_duplicates_across(
            duplicate_collection, columns=["A", "B", "C"], dup_type="all"
        )
        assert isinstance(result, ColumnCollection)

    def test_any_mode(self, duplicate_collection):
        result = remove_consecutive_duplicates_across(
            duplicate_collection, columns=["A", "B", "C"], dup_type="any"
        )
        assert isinstance(result, ColumnCollection)

    def test_subset_columns(self, duplicate_collection):
        result = remove_consecutive_duplicates_across(
            duplicate_collection, columns=["A", "C"], dup_type="all"
        )
        assert isinstance(result, ColumnCollection)

    def test_invalid_dup_type(self, duplicate_collection):
        with pytest.raises(ValueError, match="dup_typeは'all'または'any'である必要があります"):
            remove_consecutive_duplicates_across(
                duplicate_collection, columns=["A", "B"], dup_type="invalid"
            )

    def test_invalid_column(self, duplicate_collection):
        with pytest.raises(KeyError, match="列 '不存在' が存在しません"):
            remove_consecutive_duplicates_across(
                duplicate_collection, columns=["A", "不存在"]
            )

    def test_empty_collection(self):
        empty_collection = ColumnCollection(
            step=[],
            columns={
                "A": Column("1", "Column A", "N", []),
                "B": Column("2", "Column B", "kg", []),
            },
            metadata={"description": "Empty Collection"},
        )
        result = remove_consecutive_duplicates_across(empty_collection, columns=["A", "B"])
        assert isinstance(result, ColumnCollection)
        assert result.metadata == empty_collection.metadata

    def test_metadata_preserved(self, duplicate_collection):
        result = remove_consecutive_duplicates_across(duplicate_collection, columns=["A", "B"])
        assert result.metadata == duplicate_collection.metadata


class TestRemoveOutliers:
    """remove_outliers 関数の構造テスト"""

    @pytest.fixture
    def outlier_collection(self):
        return ColumnCollection(
            step=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            columns={
                "Data": Column("1", "Test Data", "N", [10.0, 10.2, 9.8, 50.0, 10.1, 10.3, 9.9, 10.2, -30.0, 10.1]),
                "Category": Column("2", "Category", "", ["A", "A", "A", "A", "B", "B", "B", "B", "B", "C"]),
            },
            metadata={"description": "Test Collection with Outliers"},
        )

    def test_basic_outlier_removal(self, outlier_collection):
        result = remove_outliers(
            outlier_collection,
            column="Data",
            window_size=3,
            threshold=0.3,
            edge_handling="asymmetric",
        )
        assert isinstance(result, ColumnCollection)

    def test_with_different_parameters(self, outlier_collection):
        result = remove_outliers(
            outlier_collection,
            column="Data",
            window_size=5,
            threshold=0.8,
            edge_handling="symmetric",
        )
        assert isinstance(result, ColumnCollection)

    def test_with_minimal_threshold(self, outlier_collection):
        result = remove_outliers(
            outlier_collection, column="Data", threshold=0.01
        )
        assert isinstance(result, ColumnCollection)

    def test_second_column_preserved(self, outlier_collection):
        result = remove_outliers(outlier_collection, column="Data", threshold=0.3)
        assert "Category" in result.columns

    def test_metadata_preserved(self, outlier_collection):
        result = remove_outliers(outlier_collection, column="Data")
        assert result.metadata == outlier_collection.metadata

    def test_invalid_column(self, outlier_collection):
        with pytest.raises(KeyError, match="列 '不存在' が存在しません"):
            remove_outliers(outlier_collection, column="不存在")

    def test_method_chain(self, outlier_collection):
        from tascpy.analytics.operations.core.stats import moving_average
        result = (
            outlier_collection.ops.remove_outliers(column="Data", threshold=0.3)
            .moving_average(column="Data", window_size=3, result_column="SmoothData")
            .end()
        )
        assert isinstance(result, ColumnCollection)
        assert "SmoothData" in result.columns


def test_search_by_value(sample_collection):
    result = search_by_value(sample_collection, "A", "==", 3)
    assert isinstance(result, list)

    result = search_by_value(sample_collection, "A", ">", 2)
    assert isinstance(result, list)

    result = search_by_value(sample_collection, "A", "<=", 3)
    assert isinstance(result, list)

    with pytest.raises(ValueError):
        search_by_value(sample_collection, "A", "invalid", 3)

    with pytest.raises(KeyError):
        search_by_value(sample_collection, "X", "==", 3)

def test_search_by_range(sample_collection):
    result = search_by_range(sample_collection, "B", 20, 40, inclusive=True)
    assert isinstance(result, list)

    result = search_by_range(sample_collection, "B", 20, 40, inclusive=False)
    assert isinstance(result, list)

    with pytest.raises(KeyError):
        search_by_range(sample_collection, "X", 20, 40)

def test_search_by_step_range(sample_collection):
    result = search_by_step_range(sample_collection, min=2, max=4, inclusive=True)
    assert isinstance(result, tuple)
    assert isinstance(result[0], list)
    assert isinstance(result[1], dict)

    result = search_by_step_range(sample_collection, min=2, max=4, inclusive=False)
    assert isinstance(result, tuple)

    _, metadata = result
    assert "operation" in metadata

def test_search_by_step_range_index_mode(sample_collection):
    result = search_by_step_range(
        sample_collection, min=1, max=3, inclusive=True, by_step_value=False
    )
    assert isinstance(result, tuple)
    assert isinstance(result[0], list)

    result = search_by_step_range(
        sample_collection, min=1, max=3, inclusive=False, by_step_value=False
    )
    assert isinstance(result, tuple)
    assert isinstance(result[0], list)

    _, metadata = result
    assert "operation" in metadata

def test_search_by_step_range_empty_result(sample_collection):
    result = search_by_step_range(sample_collection, min=10, max=20)
    assert isinstance(result, tuple)
    assert isinstance(result[0], list)

    result = search_by_step_range(
        sample_collection, min=10, max=20, by_step_value=False
    )
    assert isinstance(result, tuple)
    assert isinstance(result[0], list)

def test_search_by_condition(sample_collection):
    result = search_by_condition(
        sample_collection, lambda row: row["A"] > 2 and row["B"] < 40
    )
    assert isinstance(result, list)

    result = search_by_condition(
        sample_collection, lambda row: row["A"] % 2 == 1 and row["C"] is not None
    )
    assert isinstance(result, list)

def test_search_missing_values(sample_collection):
    result = search_missing_values(sample_collection, columns=["C"])
    assert isinstance(result, list)

    result = search_missing_values(sample_collection)
    assert isinstance(result, list)

    with pytest.raises(KeyError):
        search_missing_values(sample_collection, columns=["X"])

def test_search_top_n(sample_collection):
    result = search_top_n(sample_collection, "A", 2, descending=True)
    assert isinstance(result, list)

    result = search_top_n(sample_collection, "A", 2, descending=False)
    assert isinstance(result, list)

    with pytest.raises(KeyError):
        search_top_n(sample_collection, "X", 2)
