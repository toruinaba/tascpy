import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.step import Step

class TestColumnCollectionInvariants:
    """ColumnCollectionの行数整合性（Invariants）に関するテスト"""

    def test_init_raises_on_length_mismatch(self):
        """初期化時にステップとカラムの長さが異なるとエラーになること"""
        step_vals = [1, 2, 3]
        
        # カラムが短い
        with pytest.raises(ValueError, match="does not match Step length"):
            ColumnCollection(
                step=Step(step_vals),
                columns={"col1": [10, 20]}
            )
            
        # カラムが長い
        with pytest.raises(ValueError, match="does not match Step length"):
            ColumnCollection(
                step=Step(step_vals),
                columns={"col1": [10, 20, 30, 40]}
            )

    def test_init_valid_lengths(self):
        """長さが一致していれば正常に初期化できること"""
        step_vals = [1, 2, 3]
        col = ColumnCollection(
            step=Step(step_vals),
            columns={"col1": [10, 20, 30]}
        )
        assert len(col) == 3
        assert len(col["col1"]) == 3

    def test_add_column_raises_on_length_mismatch(self):
        """add_columnで長さが異なるとエラーになること"""
        col = ColumnCollection(
            step=Step([1, 2, 3]),
            columns={"col1": [10, 20, 30]}
        )
        
        with pytest.raises(ValueError, match="does not match Step length"):
            col.add_column("col2", [100, 200])

    def test_add_column_valid(self):
        """add_columnで長さが一致していれば追加できること"""
        col = ColumnCollection(
            step=Step([1, 2, 3]),
            columns={"col1": [10, 20, 30]}
        )
        col.add_column("col2", [100, 200, 300])
        assert "col2" in col.columns
        assert len(col["col2"]) == 3

    def test_set_step_raises_on_length_mismatch(self):
        """step setterで長さが異なるとエラーになること"""
        col = ColumnCollection(
            step=Step([1, 2, 3]),
            columns={"col1": [10, 20, 30]}
        )
        
        # 既存カラムと長さが違うステップをセットしようとする
        with pytest.raises(ValueError, match="does not match existing columns length"):
            col.step = Step([1, 2])

    def test_set_step_valid(self):
        """step setterで長さが一致していればセットできること"""
        col = ColumnCollection(
            step=Step([1, 2, 3]),
            columns={"col1": [10, 20, 30]}
        )
        # 値は違うが長さは同じ
        new_step = Step([4, 5, 6])
        col.step = new_step
        np.testing.assert_array_equal(col.step.values, [4, 5, 6])

    def test_filter_maintains_invariant(self):
        """filter操作が行数同期を維持すること"""
        col = ColumnCollection(
            step=Step([1, 2, 3, 4]),
            columns={"col1": [10, 20, 30, 40]}
        )
        # filter_by_value
        from tascpy.analytics.operations.core.filters import filter_by_value
        res = filter_by_value(col, "col1", 20)
        
        assert len(res) == 1
        assert len(res["col1"]) == 1
        np.testing.assert_array_equal(res.step.values, [2])
        
    def test_split_maintains_invariant(self):
        """split操作が行数同期を維持すること"""
        col = ColumnCollection(
            step=Step([1, 2, 3, 4]),
            columns={"col1": [10, 20, 30, 40]}
        )
        from tascpy.analytics.operations.core.select import split_at_indices
        res_list = split_at_indices(col, indices=2)
        
        assert len(res_list) == 2
        # First half
        assert len(res_list[0]) == 2
        assert len(res_list[0]["col1"]) == 2
        # Second half
        assert len(res_list[1]) == 2
        assert len(res_list[1]["col1"]) == 2
        
    def test_interpolate_maintains_invariant(self):
        """interpolate操作が全列の同期を維持すること"""
        col = ColumnCollection(
            step=Step([1.0, 2.0, 3.0]),
            columns={
                "val": [10.0, 20.0, 30.0],
                "meta": [1, 2, 3] # Non-number / treated as other
            }
        )
        from tascpy.analytics.operations.core.interpolate import interpolate
        
        # New axis: 1.5, 2.5 (2 points)
        res = interpolate(col, x_values=[1.5, 2.5])
        
        assert len(res) == 2
        assert len(res["val"]) == 2
        assert len(res["meta"]) == 2
        
        # Verify values
        np.testing.assert_array_equal(res.step.values, [1.5, 2.5])
        np.testing.assert_array_equal(res["val"].values, [15.0, 25.0])
        # Meta should be nearest neighbor
        # 1.5 -> closest to 1 or 2? 1.5 is equidistant. numpy searchsorted logic?
        # Usually rounds to ... check impl. 
        # But length must be 2.

