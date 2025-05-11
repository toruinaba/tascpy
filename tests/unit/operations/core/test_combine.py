"""Column合成操作のテスト"""

import pytest
import numpy as np
from src.tascpy.operations.core.combine import (
    switch_by_step,
    blend_by_step,
    conditional_select,
    custom_combine,
)
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.operations.proxy import CollectionOperations


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[10, 20, 30, 40, 50],
        columns={
            "A": [1.0, 2.0, 3.0, 4.0, 5.0],
            "B": [10.0, 20.0, 30.0, 40.0, 50.0],
            "C": [-1.0, -2.0, 0.0, 2.0, 3.0],
        },
        metadata={"description": "Test Collection"},
    )


@pytest.fixture
def ops(sample_collection):
    """CollectionOperationsのフィクスチャ"""
    return CollectionOperations(sample_collection)


class TestSwitchByStep:
    """switch_by_step関数のテスト"""

    def test_switch_by_index(self, sample_collection):
        """インデックス基準の切り替えテスト"""
        result = switch_by_step(
            sample_collection,
            "A",
            "B",
            step_threshold=2,  # インデックス2（ステップ値30）で切り替え
            compare_mode="index",
        )

        expected_name = "switch(A,B@2)"
        assert expected_name in result.columns
        expected = [1.0, 2.0, 30.0, 40.0, 50.0]  # インデックス0,1はA、2以降はB
        assert result[expected_name].values == expected

    def test_switch_by_value(self, sample_collection):
        """値基準の切り替えテスト"""
        result = switch_by_step(
            sample_collection,
            "A",
            "B",
            step_threshold=35,  # ステップ値35で切り替え
            compare_mode="value",
        )

        expected_name = "switch(A,B@35)"
        assert expected_name in result.columns
        expected = [1.0, 2.0, 3.0, 40.0, 50.0]  # ステップ値<35はA、>=35はB
        assert result[expected_name].values == expected

    def test_custom_result_column(self, sample_collection):
        """カスタム結果列名のテスト"""
        result = switch_by_step(
            sample_collection,
            "A",
            "B",
            step_threshold=2,
            compare_mode="index",
            result_column="CustomName",
        )

        assert "CustomName" in result.columns
        expected = [1.0, 2.0, 30.0, 40.0, 50.0]
        assert result["CustomName"].values == expected

    def test_invalid_column(self, sample_collection):
        """存在しない列名を指定した場合のテスト"""
        with pytest.raises(KeyError):
            switch_by_step(sample_collection, "NonExistent", "B", 2)

        with pytest.raises(KeyError):
            switch_by_step(sample_collection, "A", "NonExistent", 2)


class TestBlendByStep:
    """blend_by_step関数のテスト"""

    def test_linear_blend_by_index(self, sample_collection):
        """インデックス基準の線形ブレンドテスト"""
        result = blend_by_step(
            sample_collection,
            "A",
            "B",
            step_start=1,  # インデックス1から
            step_end=3,  # インデックス3まで
            compare_mode="index",
            blend_method="linear",
        )

        expected_name = "blend(A,B,1-3)"
        assert expected_name in result.columns

        # インデックス0はA、インデックス4はB、間は徐々にブレンド
        expected = [
            1.0,  # インデックス0: A
            2.0,  # インデックス1: 最初の要素 (t=0)
            3.0 * 0.5 + 30.0 * 0.5,  # インデックス2: A:Bを半々で混合 (t=0.5)
            40.0,  # インデックス3: 2番目の要素 (t=1)
            50.0,  # インデックス4: B
        ]
        assert result[expected_name].values == pytest.approx(expected)

    def test_smooth_blend(self, sample_collection):
        """スムーズブレンドのテスト"""
        result = blend_by_step(
            sample_collection,
            "A",
            "B",
            step_start=1,
            step_end=3,
            compare_mode="index",
            blend_method="smooth",
        )

        expected_name = "blend(A,B,1-3)"
        assert expected_name in result.columns

        # スムーズ関数での補間値を確認
        values = result[expected_name].values
        # インデックス0はA、インデックス4はB
        assert values[0] == pytest.approx(1.0)  # A
        assert values[4] == pytest.approx(50.0)  # B

        # 中間値は関数によって変化（詳細値は計算複雑なので近似テスト）
        # インデックス1は元の実装では最初の純粋なA（=2.0）になります
        assert values[1] == pytest.approx(2.0)
        # インデックス2は中間点 (スムーズ機能によって変化)
        assert values[2] > 3.0 and values[2] < 30.0
        # インデックス3は元の実装では純粋なB（=40.0）になります
        assert values[3] == pytest.approx(40.0)

    def test_invalid_range(self, sample_collection):
        """無効な範囲を指定した場合のテスト"""
        with pytest.raises(ValueError):
            blend_by_step(
                sample_collection,
                "A",
                "B",
                step_start=3,  # 開始が終了よりも大きい
                step_end=1,
            )

    def test_invalid_blend_method(self, sample_collection):
        """無効なブレンドメソッドを指定した場合のテスト"""
        with pytest.raises(ValueError):
            blend_by_step(
                sample_collection,
                "A",
                "B",
                step_start=1,
                step_end=3,
                blend_method="invalid_method",  # 存在しないメソッド
            )


class TestConditionalSelect:
    """conditional_select関数のテスト"""

    def test_greater_than_condition(self, sample_collection):
        """「より大きい」条件のテスト"""
        result = conditional_select(
            sample_collection, "A", "B", condition_column="C", threshold=0, compare=">"
        )

        expected_name = "select(A,B,where:C>0)"
        assert expected_name in result.columns
        # C > 0 の場合はA、そうでなければB
        expected = [10.0, 20.0, 30.0, 4.0, 5.0]
        assert result[expected_name].values == expected

    def test_equal_condition(self, sample_collection):
        """「等しい」条件のテスト"""
        result = conditional_select(
            sample_collection, "A", "B", condition_column="C", threshold=0, compare="=="
        )

        expected_name = "select(A,B,where:C==0)"
        assert expected_name in result.columns
        # C == 0 の場合はA、そうでなければB
        expected = [10.0, 20.0, 3.0, 40.0, 50.0]
        assert result[expected_name].values == expected

    def test_invalid_operator(self, sample_collection):
        """無効な比較演算子を指定した場合のテスト"""
        with pytest.raises(ValueError):
            conditional_select(
                sample_collection,
                "A",
                "B",
                condition_column="C",
                compare="invalid_operator",
            )


class TestCustomCombine:
    """custom_combine関数のテスト"""

    def test_custom_add_function(self, sample_collection):
        """カスタム加算関数のテスト"""
        result = custom_combine(
            sample_collection,
            "A",
            "B",
            combine_func=lambda x, y: x + y,
            func_name="add",
        )

        expected_name = "add(A,B)"
        assert expected_name in result.columns
        expected = [11.0, 22.0, 33.0, 44.0, 55.0]
        assert result[expected_name].values == expected

    def test_custom_max_function(self, sample_collection):
        """カスタム最大値関数のテスト"""
        result = custom_combine(
            sample_collection, "A", "C", combine_func=max, func_name="max"
        )

        expected_name = "max(A,C)"
        assert expected_name in result.columns
        expected = [1.0, 2.0, 3.0, 4.0, 5.0]  # 常にAの方が大きい
        assert result[expected_name].values == expected

    def test_advanced_function(self, sample_collection):
        """より複雑なカスタム関数のテスト"""

        def weighted_avg(x, y, weight_x=0.7, weight_y=0.3):
            return x * weight_x + y * weight_y

        # 部分関数を作成
        from functools import partial

        weighted_func = partial(weighted_avg, weight_x=0.6, weight_y=0.4)

        result = custom_combine(
            sample_collection,
            "A",
            "B",
            combine_func=weighted_func,
            func_name="weighted_avg",
        )

        expected_name = "weighted_avg(A,B)"
        assert expected_name in result.columns

        expected = []
        for i in range(len(sample_collection["A"].values)):
            expected.append(
                sample_collection["A"].values[i] * 0.6
                + sample_collection["B"].values[i] * 0.4
            )

        assert result[expected_name].values == pytest.approx(expected)
