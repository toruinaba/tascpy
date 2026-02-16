import pytest
import numpy as np
from tascpy.operations.core.search import (
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
        metadata={"test": "data"},
    )


def test_search_by_value(sample_collection):
    """search_by_valueのテスト"""
    # 等価演算子
    result = search_by_value(sample_collection, "A", "==", 3)
    assert len(result) == 1
    assert len(result) == 1
    # Check values using indices
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [3])
    np.testing.assert_array_equal(np.array(sample_collection.columns["A"].values)[result], [3])
    np.testing.assert_array_equal(np.array(sample_collection.columns["B"].values)[result], [30])

    # 大なり演算子
    result = search_by_value(sample_collection, "A", ">", 2)
    assert len(result) == 3
    assert len(result) == 3
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [3, 4, 5])
    np.testing.assert_array_equal(np.array(sample_collection.columns["A"].values)[result], [3, 4, 5])

    # 小なりイコール演算子
    result = search_by_value(sample_collection, "A", "<=", 3)
    assert len(result) == 3
    assert len(result) == 3
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [1, 2, 3])
    np.testing.assert_array_equal(np.array(sample_collection.columns["A"].values)[result], [1, 2, 3])

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
    assert len(result) == 3
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [2, 3, 4])
    np.testing.assert_array_equal(np.array(sample_collection.columns["B"].values)[result], [20, 30, 40])

    # 境界値を含まない
    result = search_by_range(sample_collection, "B", 20, 40, inclusive=False)
    assert len(result) == 1
    assert len(result) == 1
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [3])
    np.testing.assert_array_equal(np.array(sample_collection.columns["B"].values)[result], [30])

    # 存在しない列
    with pytest.raises(KeyError):
        search_by_range(sample_collection, "X", 20, 40)


def test_search_by_step_range(sample_collection):
    """search_by_step_rangeのテスト"""
    # 境界値を含む
    result = search_by_step_range(sample_collection, min=2, max=4, inclusive=True)
    # search_by_step_range returns (indices, metadata) tuple
    indices = result[0]
    assert len(indices) == 3
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[indices], [2, 3, 4])

    # 境界値を含まない
    result = search_by_step_range(sample_collection, min=2, max=4, inclusive=False)
    indices = result[0]
    assert len(indices) == 1
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[indices], [3])

    # メタデータに操作情報が記録されていることを確認
    # メタデータに操作情報が記録されていることを確認
    _, metadata = result
    assert "operation" in metadata
    assert metadata["operation"] == "search_by_step_range"
    assert metadata["by_step_value"] is True


# 拡張機能のテスト
def test_search_by_step_range_index_mode(sample_collection):
    """インデックスによる範囲検索のテスト（by_step_value=False）"""
    # 境界値を含む
    result = search_by_step_range(
        sample_collection, min=1, max=3, inclusive=True, by_step_value=False
    )
    # インデックス1～3（ステップ値 2, 3, 4）が選択される
    # インデックス1～3（ステップ値 2, 3, 4）が選択される
    indices = result[0]
    assert len(indices) == 3
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[indices], [2, 3, 4])

    # 境界値を含まない
    result = search_by_step_range(
        sample_collection, min=1, max=3, inclusive=False, by_step_value=False
    )
    # インデックス2（ステップ値 3）のみ選択される
    # インデックス2（ステップ値 3）のみ選択される
    indices = result[0]
    assert len(indices) == 1
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[indices], [3])

    # メタデータに操作情報が記録されていることを確認
    # メタデータに操作情報が記録されていることを確認
    _, metadata = result
    assert "operation" in metadata
    assert metadata["operation"] == "search_by_step_range"
    assert metadata["by_step_value"] is False


def test_search_by_step_range_empty_result(sample_collection):
    """検索結果が空の場合のテスト"""
    # 範囲外の値を指定
    result = search_by_step_range(sample_collection, min=10, max=20)
    # 空の結果が返される
    # 空の結果が返される
    indices = result[0]
    assert len(indices) == 0

    # インデックスモードで範囲外を指定
    result = search_by_step_range(
        sample_collection, min=10, max=20, by_step_value=False
    )
    # 空の結果が返される
    # 空の結果が返される
    indices = result[0]
    assert len(indices) == 0


def test_search_by_condition(sample_collection):
    """search_by_conditionのテスト"""
    # 複数条件での検索
    result = search_by_condition(
        sample_collection, lambda row: row["A"] > 2 and row["B"] < 40
    )
    assert len(result) == 1
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [3])
    np.testing.assert_array_equal(np.array(sample_collection.columns["A"].values)[result], [3])
    np.testing.assert_array_equal(np.array(sample_collection.columns["B"].values)[result], [30])

    # 複雑な条件
    result = search_by_condition(
        sample_collection, lambda row: row["A"] % 2 == 1 and row["C"] is not None
    )
    assert len(result) == 3
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [1, 3, 5])


def test_search_missing_values(sample_collection):
    """search_missing_valuesのテスト"""
    # 特定の列での欠損値検索
    result = search_missing_values(sample_collection, columns=["C"])
    assert len(result) == 2
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [2, 4])

    # 全列での欠損値検索
    result = search_missing_values(sample_collection)
    assert len(result) == 2
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [2, 4])

    # 存在しない列
    with pytest.raises(KeyError):
        search_missing_values(sample_collection, columns=["X"])


def test_search_top_n(sample_collection):
    """search_top_nのテスト"""
    # 降順でのトップN検索
    result = search_top_n(sample_collection, "A", 2, descending=True)
    assert len(result) == 2
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [4, 5])
    np.testing.assert_array_equal(np.array(sample_collection.columns["A"].values)[result], [4, 5])

    # 昇順でのトップN検索
    result = search_top_n(sample_collection, "A", 2, descending=False)
    assert len(result) == 2
    np.testing.assert_array_equal(np.array(sample_collection.step.values)[result], [1, 2])
    np.testing.assert_array_equal(np.array(sample_collection.columns["A"].values)[result], [1, 2])

    # 存在しない列
    with pytest.raises(KeyError):
        search_top_n(sample_collection, "X", 2)
