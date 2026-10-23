import pytest
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "A": Column("Column A", ch="1", unit="N", values=[1, 2, 3, 4, 5]),
            "B": Column("Column B", ch="2", unit="kg", values=[10, 20, 30, 40, 50]),
            "C": Column("Column C", ch="3", unit="m", values=[100, None, 300, None, 500]),
        },
        metadata={"description": "Test Collection"},
    )


class TestFilterByValue:
    """filter_by_value関数の構造テスト"""

    def test_exact_match(self, sample_collection):
        result = sample_collection.ops.filter_by_value("A", 3).end()
        assert isinstance(result, ColumnCollection)
        assert "A" in result.columns
        assert result.metadata == sample_collection.metadata

    def test_tolerance_filter(self, sample_collection):
        result = sample_collection.ops.filter_by_value("A", 3, tolerance=1.0).end()
        assert isinstance(result, ColumnCollection)

    def test_no_match(self, sample_collection):
        result = sample_collection.ops.filter_by_value("A", 100).end()
        assert isinstance(result, ColumnCollection)

    def test_invalid_column(self, sample_collection):
        with pytest.raises(KeyError, match="列 '不存在' が存在しません"):
            sample_collection.ops.filter_by_value("不存在", 1).end()


class TestFilterOutNone:
    """filter_out_none関数の構造テスト"""

    def test_filter_all_columns_any_mode(self, sample_collection):
        result = sample_collection.ops.filter_out_none().end()
        assert isinstance(result, ColumnCollection)

    def test_filter_specific_columns(self, sample_collection):
        result = sample_collection.ops.filter_out_none(columns=["C"]).end()
        assert isinstance(result, ColumnCollection)
        assert "A" in result.columns

    def test_filter_all_mode(self, sample_collection):
        extended_collection = ColumnCollection(
            step=[1, 2, 3, 4, 5, 6],
            columns={
                "A": Column("Column A", ch="1", unit="N", values=[1, 2, None, 4, 5, None]),
                "B": Column("Column B", ch="2", unit="kg", values=[10, None, None, 40, 50, None]),
                "C": Column("Column C", ch="3", unit="m", values=[100, None, 300, None, 500, None]),
            },
            metadata=sample_collection.metadata,
        )
        result = extended_collection.ops.filter_out_none(mode="all").end()
        assert isinstance(result, ColumnCollection)

    def test_invalid_column(self, sample_collection):
        with pytest.raises(KeyError, match="列 '不存在' が存在しません"):
            sample_collection.ops.filter_out_none(columns=["A", "不存在"]).end()

    def test_invalid_mode(self, sample_collection):
        with pytest.raises(ValueError, match="mode は 'any' または 'all' で指定してください"):
            sample_collection.ops.filter_out_none(mode="invalid").end()

    def test_metadata_preserved(self, sample_collection):
        result = sample_collection.ops.filter_out_none().end()
        assert result.metadata == sample_collection.metadata


class TestRemoveConsecutiveDuplicatesAcross:
    """remove_consecutive_duplicates_across関数の構造テスト"""

    @pytest.fixture
    def duplicate_collection(self):
        return ColumnCollection(
            step=[1, 2, 3, 4, 5, 6, 7, 8],
            columns={
                "A": Column("Column A", ch="1", unit="N", values=[1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0]),
                "B": Column("Column B", ch="2", unit="kg", values=[10.0, 20.0, 30.0, 30.0, 40.0, 50.0, 60.0, 60.0]),
                "C": Column("Column C", ch="3", unit="m", values=[5, 5, 2, 2, 8, 8, 9, 10]),
            },
            metadata={"description": "Test Collection with Duplicates"},
        )

    def test_removes_rows_identical_to_previous(self, duplicate_collection):
        result = duplicate_collection.ops.remove_consecutive_duplicates_across(columns=["A", "C"]).end()
        assert result.step.tolist() == [1, 3, 5, 7, 8]

    def test_all_columns(self, duplicate_collection):
        result = duplicate_collection.ops.remove_consecutive_duplicates_across(columns=["A", "B", "C"]
        ).end()
        assert isinstance(result, ColumnCollection)

    def test_subset_columns(self, duplicate_collection):
        result = duplicate_collection.ops.remove_consecutive_duplicates_across(columns=["A", "C"]
        ).end()
        assert isinstance(result, ColumnCollection)

    def test_invalid_column(self, duplicate_collection):
        with pytest.raises(KeyError, match="列 '不存在' が存在しません"):
            duplicate_collection.ops.remove_consecutive_duplicates_across(columns=["A", "不存在"]
            ).end()

    def test_empty_collection(self):
        empty_collection = ColumnCollection(
            step=[],
            columns={
                "A": Column("Column A", ch="1", unit="N", values=[]),
                "B": Column("Column B", ch="2", unit="kg", values=[]),
            },
            metadata={"description": "Empty Collection"},
        )
        result = empty_collection.ops.remove_consecutive_duplicates_across(columns=["A", "B"]).end()
        assert isinstance(result, ColumnCollection)
        assert result.metadata == empty_collection.metadata

    def test_metadata_preserved(self, duplicate_collection):
        result = duplicate_collection.ops.remove_consecutive_duplicates_across(columns=["A", "B"]).end()
        assert result.metadata == duplicate_collection.metadata


class TestRemoveOutliers:
    """remove_outliers 関数の構造テスト"""

    @pytest.fixture
    def outlier_collection(self):
        return ColumnCollection(
            step=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            columns={
                "Data": Column("Test Data", ch="1", unit="N", values=[10.0, 10.2, 9.8, 50.0, 10.1, 10.3, 9.9, 10.2, -30.0, 10.1]),
                "Category": Column("Category", ch="2", unit="", values=["A", "A", "A", "A", "B", "B", "B", "B", "B", "C"]),
            },
            metadata={"description": "Test Collection with Outliers"},
        )

    def test_basic_outlier_removal(self, outlier_collection):
        result = outlier_collection.ops.remove_outliers(column="Data",
            window_size=3,
            threshold=0.3,
            edge_handling="asymmetric",
        ).end()
        assert isinstance(result, ColumnCollection)

    def test_with_different_parameters(self, outlier_collection):
        result = outlier_collection.ops.remove_outliers(column="Data",
            window_size=5,
            threshold=0.8,
            edge_handling="symmetric",
        ).end()
        assert isinstance(result, ColumnCollection)

    def test_with_minimal_threshold(self, outlier_collection):
        result = outlier_collection.ops.remove_outliers(column="Data", threshold=0.01
        ).end()
        assert isinstance(result, ColumnCollection)

    def test_second_column_preserved(self, outlier_collection):
        result = outlier_collection.ops.remove_outliers(column="Data", threshold=0.3).end()
        assert "Category" in result.columns

    def test_metadata_preserved(self, outlier_collection):
        result = outlier_collection.ops.remove_outliers(column="Data").end()
        assert result.metadata == outlier_collection.metadata

    def test_invalid_column(self, outlier_collection):
        with pytest.raises(KeyError, match="列 '不存在' が存在しません"):
            outlier_collection.ops.remove_outliers(column="不存在").end()

    def test_method_chain(self, outlier_collection):
        result = (
            outlier_collection.ops.remove_outliers(column="Data", threshold=0.3)
            .moving_average(column="Data", window_size=3, result_column="SmoothData")
            .end()
        )
        assert isinstance(result, ColumnCollection)
        assert "SmoothData" in result.columns


