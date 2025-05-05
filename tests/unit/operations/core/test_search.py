import pytest
from src.tascpy.operations.core.search import (
    search_by_value,
    search_by_range,
    search_by_step_range,
    search_by_condition,
    search_missing_values,
    search_top_n,
)
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column


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
        metadata={"test": "data"}
    )


def test_search_by_value(sample_collection):
    """search_by_valueのテスト"""
    # 等価演算子
    result = search_by_value(sample_collection, "A", "==", 3)
    assert len(result) == 1
    assert result.step.values == [3]
    assert result.columns["A"].values == [3]
    assert result.columns["B"].values == [30]
    
    # 大なり演算子
    result = search_by_value(sample_collection, "A", ">", 2)
    assert len(result) == 3
    assert result.step.values == [3, 4, 5]
    assert result.columns["A"].values == [3, 4, 5]
    
    # 小なりイコール演算子
    result = search_by_value(sample_collection, "A", "<=", 3)
    assert len(result) == 3
    assert result.step.values == [1, 2, 3]
    assert result.columns["A"].values == [1, 2, 3]
    
    # 不正な演算子
    with pytest.raises(ValueError):
        search_by_value(sample_collection, "A", "invalid", 3)
    
    # 存在しない列
    with pytest.raises(KeyError):
        search_by_value(sample_collection, "X", "==", 3)


def test_search_by_range(sample_collection):
    """search_by_rangeのテスト"""
    # 境界値を含む
    result = search_by_range(sample_collection, "B", 20, 40, inclusive=True)
    assert len(result) == 3
    assert result.step.values == [2, 3, 4]
    assert result.columns["B"].values == [20, 30, 40]
    
    # 境界値を含まない
    result = search_by_range(sample_collection, "B", 20, 40, inclusive=False)
    assert len(result) == 1
    assert result.step.values == [3]
    assert result.columns["B"].values == [30]
    
    # 存在しない列
    with pytest.raises(KeyError):
        search_by_range(sample_collection, "X", 20, 40)


def test_search_by_step_range(sample_collection):
    """search_by_step_rangeのテスト"""
    # 境界値を含む
    result = search_by_step_range(sample_collection, 2, 4, inclusive=True)
    assert len(result) == 3
    assert result.step.values == [2, 3, 4]
    
    # 境界値を含まない
    result = search_by_step_range(sample_collection, 2, 4, inclusive=False)
    assert len(result) == 1
    assert result.step.values == [3]


def test_search_by_condition(sample_collection):
    """search_by_conditionのテスト"""
    # 複数条件での検索
    result = search_by_condition(sample_collection, lambda row: row["A"] > 2 and row["B"] < 40)
    assert len(result) == 1
    assert result.step.values == [3]
    assert result.columns["A"].values == [3]
    assert result.columns["B"].values == [30]
    
    # 複雑な条件
    result = search_by_condition(
        sample_collection, 
        lambda row: row["A"] % 2 == 1 and row["C"] is not None
    )
    assert len(result) == 3
    assert result.step.values == [1, 3, 5]


def test_search_missing_values(sample_collection):
    """search_missing_valuesのテスト"""
    # 特定の列での欠損値検索
    result = search_missing_values(sample_collection, ["C"])
    assert len(result) == 2
    assert result.step.values == [2, 4]
    
    # 全列での欠損値検索
    result = search_missing_values(sample_collection)
    assert len(result) == 2
    assert result.step.values == [2, 4]
    
    # 存在しない列
    with pytest.raises(KeyError):
        search_missing_values(sample_collection, ["X"])


def test_search_top_n(sample_collection):
    """search_top_nのテスト"""
    # 降順でのトップN検索
    result = search_top_n(sample_collection, "A", 2, descending=True)
    assert len(result) == 2
    assert result.step.values == [4, 5]
    assert result.columns["A"].values == [4, 5]
    
    # 昇順でのトップN検索
    result = search_top_n(sample_collection, "A", 2, descending=False)
    assert len(result) == 2
    assert result.step.values == [1, 2]
    assert result.columns["A"].values == [1, 2]
    
    # 存在しない列
    with pytest.raises(KeyError):
        search_top_n(sample_collection, "X", 2)