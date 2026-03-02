"""
select 操作のテスト
"""

import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.analytics.operations.proxy import CollectionOperations
from tascpy.analytics.operations.core.select import select


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "A": Column("1", "Column A", "", [10, 20, 30, 40, 50]),
            "B": Column("2", "Column B", "", [1.1, 2.2, 3.3, 4.4, 5.5]),
            "C": Column("3", "Column C", "", ["a", "b", "c", "d", "e"]),
        },
        metadata={"description": "Test Collection for Select Operations"},
    )


@pytest.fixture
def ops(sample_collection):
    """CollectionOperationsのフィクスチャ"""
    return CollectionOperations(sample_collection)


class TestSelect:
    """select 関数の構造テスト"""

    def test_select_columns(self, sample_collection):
        result = select(sample_collection, columns=["A", "C"])
        assert isinstance(result, ColumnCollection)
        assert list(result.columns.keys()) == ["A", "C"]
        assert len(result) == 5

    def test_select_indices(self, sample_collection):
        result = select(sample_collection, indices=[0, 2, 4])
        assert isinstance(result, ColumnCollection)
        assert len(result) == 3

    def test_select_both(self, sample_collection):
        result = select(sample_collection, columns=["B", "C"], indices=[1, 3])
        assert isinstance(result, ColumnCollection)
        assert list(result.columns.keys()) == ["B", "C"]
        assert len(result) == 2

    def test_select_by_steps(self, sample_collection):
        result = select(sample_collection, steps=[1, 3, 5])
        assert isinstance(result, ColumnCollection)
        assert len(result) == 3
        assert result.metadata["operation"] == "select_step"

    def test_select_with_tolerance(self, sample_collection):
        result = select(sample_collection, steps=[1.2, 3.1, 4.95], tolerance=0.2)
        assert isinstance(result, ColumnCollection)
        assert len(result) == 3

    def test_select_by_index(self, sample_collection):
        result = select(sample_collection, steps=[0, 2, 4], by_step_value=False)
        assert len(result) == 3
        assert "by_step_value" in result.metadata
        assert result.metadata["by_step_value"] is False

    def test_nonexistent_column(self, sample_collection):
        with pytest.raises(KeyError, match="列 'X' が存在しません"):
            select(sample_collection, columns=["A", "X"])

    def test_invalid_index(self, sample_collection):
        with pytest.raises(IndexError, match="指定されたインデックスが範囲外です"):
            select(sample_collection, indices=[0, 10])

    def test_both_indices_and_steps_not_allowed(self, sample_collection):
        with pytest.raises(ValueError, match="indicesとstepsは同時に指定できません"):
            select(sample_collection, indices=[0, 1], steps=[2, 3])

from tascpy.analytics.operations.core.select import split_by_integers, split_at_indices
from tascpy.analytics.operations.list_proxy import CollectionListOperations

def test_split_by_integers_structure(sample_collection):
    markers = [1, 2, 1, 3, 2]
    result = split_by_integers(sample_collection, markers)
    assert isinstance(result, list)
    assert len(result) == 3
    for r in result:
        assert isinstance(r, ColumnCollection)

def test_split_by_integers_preserves_metadata(sample_collection):
    sample_collection.metadata = {"source": "test", "date": "2025-05-03"}
    markers = [1, 2, 1, 2, 1]
    result = split_by_integers(sample_collection, markers)
    assert len(result) == 2
    assert result[0].metadata == {"source": "test", "date": "2025-05-03"}

def test_split_by_integers_with_proxy(sample_collection):
    markers = [1, 2, 1, 3, 2]
    result = sample_collection.ops.split_by_integers(markers)
    assert isinstance(result, CollectionListOperations)
    assert len(result) == 3
    first_two = result[:2]
    assert isinstance(first_two, CollectionListOperations)
    assert len(first_two) == 2

def test_split_at_indices_structure(sample_collection):
    result = split_at_indices(sample_collection, indices=[2])
    assert isinstance(result, list)
    assert len(result) == 2
    for r in result:
        assert isinstance(r, ColumnCollection)

