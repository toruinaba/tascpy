"""
select および select_step の機能テスト

実際のユースケースに基づいた機能テストを行います。
"""

import pytest
import numpy as np

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column





def test_select_with_operations_chain(large_collection):
    """select と他の操作をチェーンして使用するテスト"""
    ops = large_collection.ops

    # まず列を選択
    cols_selected = ops.select(columns=["Force", "Displacement"]).end()

    # 次に行を選択
    ops2 = cols_selected.ops
    result = ops2.select(indices=list(range(0, 50, 5))).end()  # 0, 5, 10, ... , 45

    # 結果の検証
    assert len(result) == 10  # 50/5 = 10 rows
    assert list(result.columns) == ["Force", "Displacement"]
    assert list(result.step) == [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    expected_force = [0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0, 22.5]
    assert list(result["Force"].values) == expected_force

    # 新しい統合されたselect関数を使った場合のテスト
    ops3 = large_collection.ops
    combined_result = ops3.select(
        columns=["Force", "Displacement"], indices=list(range(0, 50, 5))
    ).end()

    # 両方の結果が同じであることを検証
    assert len(combined_result) == len(result)
    assert list(combined_result.columns) == list(result.columns)
    assert list(combined_result.step) == list(result.step)
    assert list(combined_result["Force"].values) == list(result["Force"].values)
    assert list(combined_result["Displacement"].values) == list(
        result["Displacement"].values
    )


def test_select_step_with_operations_chain(large_collection):
    """select_step と他の操作をチェーンして使用するテスト"""
    ops = large_collection.ops

    # 特定のステップと列を選択
    result = ops.select(
        steps=[10, 20, 30, 40, 50], columns=["Time", "Temperature"]
    ).end()

    # 結果の検証
    assert len(result) == 5
    assert list(result.columns) == ["Time", "Temperature"]
    assert list(result["Time"].values) == [10, 20, 30, 40, 50]
    np.testing.assert_allclose(result["Temperature"].values, [21.0, 22.0, 23.0, 24.0, 25.0])
    assert result.units == {"Time": "s", "Temperature": "C"}

    # 新しいselect関数を使った場合も同じ結果が得られることを確認
    result2 = ops.select(steps=[10, 20, 30, 40, 50], columns=["Time", "Temperature"]).end()
    assert len(result2) == 5
    assert list(result2.columns) == ["Time", "Temperature"]
    assert list(result2["Time"].values) == list(result["Time"].values)
    assert list(result2["Temperature"].values) == list(result["Temperature"].values)

def test_sequential_select_operations(large_collection):
    """複数のselect操作を順番に実行するテスト"""
    ops = large_collection.ops

    # まず列を選択
    cols_selected = ops.select(columns=["Force", "Temperature"]).end()
    assert list(cols_selected.columns) == ["Force", "Temperature"]

    # 次に行を選択
    ops2 = cols_selected.ops
    rows_selected = ops2.select(indices=[10, 20, 30]).end()

    # 結果の検証
    assert len(rows_selected) == 3
    assert list(rows_selected.step) == [10, 20, 30]
    assert list(rows_selected["Force"].values) == [5.0, 10.0, 15.0]

    # 統合されたselect関数で一度に行と列を選択
    ops3 = large_collection.ops
    combined_result = ops3.select(
        columns=["Force", "Temperature"], indices=[10, 20, 30]
    ).end()

    # 結果の検証（同じ結果になるはず）
    assert len(combined_result) == 3
    assert list(combined_result.columns) == ["Force", "Temperature"]
    assert list(combined_result.step) == list(rows_selected.step)
    assert list(combined_result["Force"].values) == list(rows_selected["Force"].values)
    assert list(combined_result["Temperature"].values) == list(
        rows_selected["Temperature"].values
    )


def test_select_and_transform(large_collection):
    """select操作後に変換を適用するテスト"""
    ops = large_collection.ops

    # 一部の列を選択
    cols_result = ops.select(columns=["Force", "Displacement"]).end()

    # 特定のステップを選択
    ops2 = cols_result.ops
    result = ops2.select(steps=list(range(0, 50, 10))).end()  # 0, 10, 20, 30, 40

    assert list(result.step) == [0, 10, 20, 30, 40]
    assert result["Force"].unit == "N"

    # 新しいselect関数を使った場合のテスト - 1回の呼び出しで列とステップ両方を指定
    ops4 = large_collection.ops
    result2 = ops4.select(
        columns=["Force", "Displacement"],
        steps=list(range(0, 50, 10)),  # 0, 10, 20, 30, 40
    ).end()

    assert len(result2) == 5
    assert list(result2.columns) == ["Force", "Displacement"]
    assert list(result2.step) == [0, 10, 20, 30, 40]
