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
    """select 関数のテスト"""

    def test_select_columns(self, sample_collection):
        """列の選択テスト"""
        result = select(sample_collection, columns=["A", "C"])

        # 結果の検証
        assert list(result.columns.keys()) == ["A", "C"]
        assert len(result) == 5
        assert list(result["A"].values) == [10, 20, 30, 40, 50]
        assert list(result["C"].values) == ["a", "b", "c", "d", "e"]

    def test_select_indices(self, sample_collection):
        """行インデックスの選択テスト"""
        result = select(sample_collection, indices=[0, 2, 4])

        # 結果の検証
        assert len(result) == 3
        assert list(result.step.values) == [1, 3, 5]
        assert list(result["A"].values) == [10, 30, 50]
        assert list(result["B"].values) == [1.1, 3.3, 5.5]
        assert list(result["C"].values) == ["a", "c", "e"]

    def test_select_both(self, sample_collection):
        """列と行の両方を選択するテスト"""
        result = select(sample_collection, columns=["B", "C"], indices=[1, 3])

        # 結果の検証
        assert list(result.columns.keys()) == ["B", "C"]
        assert len(result) == 2
        assert list(result.step.values) == [2, 4]
        assert list(result["B"].values) == [2.2, 4.4]
        assert list(result["C"].values) == ["b", "d"]

    def test_nonexistent_column(self, sample_collection):
        """存在しない列名を指定した場合のテスト"""
        with pytest.raises(KeyError, match="列 'X' が存在しません"):
            select(sample_collection, columns=["A", "X"])

    def test_invalid_index(self, sample_collection):
        """範囲外のインデックスを指定した場合のテスト"""
        with pytest.raises(IndexError, match="指定されたインデックスが範囲外です"):
            select(sample_collection, indices=[0, 10])

    def test_select_by_steps(self, sample_collection):
        """ステップ値による選択テスト"""
        result = select(sample_collection, steps=[1, 3, 5])

        # 結果の検証
        assert len(result) == 3
        assert list(result.step.values) == [1, 3, 5]
        assert list(result["A"].values) == [10, 30, 50]
        assert result.metadata["operation"] == "select_step"

    def test_select_by_steps_and_columns(self, sample_collection):
        """ステップ値と列の両方を選択するテスト"""
        result = select(sample_collection, columns=["A", "C"], steps=[2, 4])

        # 結果の検証
        assert list(result.columns.keys()) == ["A", "C"]
        assert len(result) == 2
        assert list(result.step.values) == [2, 4]
        assert list(result["A"].values) == [20, 40]
        assert list(result["C"].values) == ["b", "d"]

    def test_nonexistent_step(self, sample_collection):
        """存在しないステップを指定した場合のテスト - 存在しないステップは無視される"""
        result = select(sample_collection, steps=[1, 6])

        # 結果の検証 - 存在するステップのみが選択される
        assert len(result) == 1
        assert result.step.values == [1]
        assert "missing_steps" in result.metadata
        assert result.metadata["missing_steps"] == [6]

    def test_select_by_index(self, sample_collection):
        """インデックスによる選択テスト（by_step_value=False）"""
        result = select(sample_collection, steps=[0, 2, 4], by_step_value=False)

        # 結果の検証
        assert len(result) == 3
        assert list(result.step.values) == [
            1,
            3,
            5,
        ]  # インデックス0,2,4に対応するステップ値
        assert list(result["A"].values) == [10, 30, 50]
        assert "by_step_value" in result.metadata
        assert result.metadata["by_step_value"] is False

    def test_select_with_tolerance(self, sample_collection):
        """許容範囲を指定した選択テスト"""
        # ステップ値にない値（1.2, 3.1, 4.95）を指定し、許容範囲内のステップ値を選択
        result = select(sample_collection, steps=[1.2, 3.1, 4.95], tolerance=0.2)

        # 結果の検証
        assert len(result) == 3
        assert list(result.step.values) == [1, 3, 5]  # 許容範囲内の値が選択される
        assert list(result["A"].values) == [10, 30, 50]

    def test_select_with_tolerance_no_match(self, sample_collection):
        """許容範囲を指定しても見つからない場合のテスト"""
        result = select(sample_collection, steps=[6.5, 7.5], tolerance=0.1)

        # 結果の検証 - 一致するステップが見つからないので空のコレクション
        assert len(result) == 0
        assert len(result.step.values) == 0
        assert "missing_steps" in result.metadata
        assert sorted(result.metadata["missing_steps"]) == [6.5, 7.5]

    def test_select_by_step_out_of_range(self, sample_collection):
        """範囲外のインデックスを指定した場合のテスト (stepsパラメータ使用時)"""
        result = select(sample_collection, steps=[-1, 10], by_step_value=False)

        # 結果の検証 - 範囲外のインデックスは無視される（エラーにならない）
        assert len(result) == 0
        assert len(result.step.values) == 0
        assert "missing_steps" in result.metadata
        assert sorted(result.metadata["missing_steps"]) == [-1, 10]

    def test_both_indices_and_steps_not_allowed(self, sample_collection):
        """indicesとstepsの両方を指定した場合のテスト"""
        with pytest.raises(ValueError, match="indicesとstepsは同時に指定できません"):
            select(sample_collection, indices=[0, 1], steps=[2, 3])

# --- split operations tests ---
from tascpy.analytics.operations.core.select import split_by_integers, split_at_indices
from tascpy.analytics.operations.list_proxy import CollectionListOperations

def test_split_by_integers_basic(sample_collection):
    """split_by_integersの基本機能をテスト"""
    # 3つのグループに分割
    markers = [1, 2, 1, 3, 2]  # 1=グループ1, 2=グループ2, 3=グループ3
    result = split_by_integers(sample_collection, markers)

    # 結果検証
    assert len(result) == 3  # 3つのグループができているか

    # グループ1 (marker=1) の検証
    np.testing.assert_array_equal(result[0].step.values, [1, 3])
    np.testing.assert_array_equal(result[0].columns["A"].values, [10, 30])
    np.testing.assert_array_equal(result[0].columns["B"].values, [1.1, 3.3])

    # グループ2 (marker=2) の検証
    np.testing.assert_array_equal(result[1].step.values, [2, 5])
    np.testing.assert_array_equal(result[1].columns["A"].values, [20, 50])
    np.testing.assert_array_equal(result[1].columns["B"].values, [2.2, 5.5])

    # グループ3 (marker=3) の検証
    np.testing.assert_array_equal(result[2].step.values, [4])
    np.testing.assert_array_equal(result[2].columns["A"].values, [40])
    np.testing.assert_array_equal(result[2].columns["B"].values, [4.4])


def test_split_by_integers_single_marker(sample_collection):
    """単一マーカー値での分割をテスト"""
    # すべて同じマーカー値で分割
    markers = [1, 1, 1, 1, 1]
    result = split_by_integers(sample_collection, markers)

    # 結果検証
    assert len(result) == 1  # 1つのグループができる
    np.testing.assert_array_equal(result[0].step.values, [1, 2, 3, 4, 5])  # 元のステップと同じ
    np.testing.assert_array_equal(result[0].columns["A"].values, [10, 20, 30, 40, 50])  # 元の値と同じ
    np.testing.assert_array_equal(result[0].columns["B"].values, [1.1, 2.2, 3.3, 4.4, 5.5])  # 元の値と同じ


def test_split_by_integers_preserves_metadata(sample_collection):
    """メタデータが保持されることを確認するテスト"""
    # メタデータの追加
    sample_collection.metadata = {"source": "test", "date": "2025-05-03"}

    # 分割実行
    markers = [1, 2, 1, 2, 1]
    result = split_by_integers(sample_collection, markers)

    # 結果検証
    assert len(result) == 2
    assert result[0].metadata == {"source": "test", "date": "2025-05-03"}
    assert result[1].metadata == {"source": "test", "date": "2025-05-03"}


def test_split_by_integers_error_length_mismatch(sample_collection):
    """データとマーカーの長さが一致しない場合のエラーをテスト"""
    # マーカーの長さが短い場合
    with pytest.raises(ValueError) as err_short:
        split_by_integers(sample_collection, [1, 2, 3])
    assert "長さは一致する必要があります" in str(err_short.value)

    # マーカーの長さが長い場合
    with pytest.raises(ValueError) as err_long:
        split_by_integers(sample_collection, [1, 2, 3, 4, 5, 6, 7])
    assert "長さは一致する必要があります" in str(err_long.value)


def test_split_by_integers_with_proxy(sample_collection):
    """プロキシクラス経由でsplit_by_integersを使用するテスト"""
    # プロキシ経由で分割
    markers = [1, 2, 1, 3, 2]
    result = sample_collection.ops.split_by_integers(markers)

    # 結果がCollectionListOperationsであることを確認
    assert isinstance(result, CollectionListOperations)
    assert len(result) == 3

    # 個々のコレクションにアクセス
    first_group = result[0]
    from tascpy.analytics.operations.proxy import CollectionOperations
    assert isinstance(first_group, CollectionOperations)
    np.testing.assert_array_equal(first_group.end().step.values, [1, 3])
    np.testing.assert_array_equal(first_group.end().columns["A"].values, [10, 30])

    # スライスでのアクセスをテスト
    first_two = result[:2]
    assert isinstance(first_two, CollectionListOperations)
    assert len(first_two) == 2


def test_split_by_integers_and_method_chain(sample_collection):
    """メソッドチェーンでの操作をテスト"""
    # 分割した結果に対してフィルタリング操作を適用
    markers = [1, 2, 3, 1, 2]

    # 最初の要素だけを取得（インデックス付きアクセス）
    first_group = sample_collection.ops.split_by_integers(markers)[0]
    from tascpy.analytics.operations.proxy import CollectionOperations
    assert isinstance(first_group, CollectionOperations)

    # 分割した結果に個別にアクセスして操作
    result = sample_collection.ops.split_by_integers(markers)

    # 個々のグループに対して操作
    group1 = result[0].end()
    assert len(group1) == 2  # マーカー1は2つある
    np.testing.assert_array_equal(group1.step.values, [1, 4])

    group2 = result[1].end()
    assert len(group2) == 2  # マーカー2は2つある
    np.testing.assert_array_equal(group2.step.values, [2, 5])

    group3 = result[2].end()
    assert len(group3) == 1  # マーカー3は1つある
    np.testing.assert_array_equal(group3.step.values, [3])
