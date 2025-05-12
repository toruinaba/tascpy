"""
select 操作のテスト
"""

import pytest
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column
from src.tascpy.operations.proxy import CollectionOperations
from src.tascpy.operations.core.select import select, select_step


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
        assert list(result.step.values) == [1, 3, 5]  # インデックス0,2,4に対応するステップ値
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
        assert result.step.values == []
        assert "missing_steps" in result.metadata
        assert sorted(result.metadata["missing_steps"]) == [6.5, 7.5]

    def test_select_by_step_out_of_range(self, sample_collection):
        """範囲外のインデックスを指定した場合のテスト (stepsパラメータ使用時)"""
        result = select(sample_collection, steps=[-1, 10], by_step_value=False)

        # 結果の検証 - 範囲外のインデックスは無視される（エラーにならない）
        assert len(result) == 0
        assert result.step.values == []
        assert "missing_steps" in result.metadata
        assert sorted(result.metadata["missing_steps"]) == [-1, 10]

    def test_both_indices_and_steps_not_allowed(self, sample_collection):
        """indicesとstepsの両方を指定した場合のテスト"""
        with pytest.raises(ValueError, match="indicesとstepsは同時に指定できません"):
            select(sample_collection, indices=[0, 1], steps=[2, 3])

    def test_legacy_select_step(self, sample_collection):
        """旧select_step関数の互換性テスト"""
        # 旧関数を使用
        result = select_step(sample_collection, steps=[2, 4], columns=["A", "C"])

        # 新しいselect関数と同じ結果が得られるか検証
        expected = select(sample_collection, steps=[2, 4], columns=["A", "C"])
        
        assert list(result.columns.keys()) == list(expected.columns.keys())
        assert result.step.values == expected.step.values
        # オブジェクト自体ではなく、値を比較する
        assert list(result["A"].values) == list(expected["A"].values)
        assert list(result["C"].values) == list(expected["C"].values)
        assert result.metadata["operation"] == expected.metadata["operation"]
