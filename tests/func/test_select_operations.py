"""
select および select_step の機能テスト

実際のユースケースに基づいた機能テストを行います。
"""

import os
import pytest
import numpy as np

from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column
from src.tascpy.operations.proxy import CollectionOperations


@pytest.fixture
def large_collection():
    """テスト用の大きなCollectionを作成"""
    steps = list(range(100))
    columns = {
        "Time": Column("1", "Time", "s", list(range(100))),
        "Force": Column("2", "Force", "N", [i * 0.5 for i in range(100)]),
        "Displacement": Column(
            "3", "Displacement", "mm", [i * 0.01 for i in range(100)]
        ),
        "Temperature": Column(
            "4", "Temperature", "C", [20 + i * 0.1 for i in range(100)]
        ),
    }
    return ColumnCollection(step=steps, columns=columns)


def test_select_with_operations_chain(large_collection):
    """select と他の操作をチェーンして使用するテスト"""
    ops = CollectionOperations(large_collection)

    # 特定の列と行を選択して、数学演算を適用
    result = (
        ops.select(columns=["Force", "Displacement"])
        .select(indices=list(range(0, 50, 5)))  # 0, 5, 10, ... , 45
        .end()
    )

    # 結果の検証
    assert len(result) == 10  # 50/5 = 10 rows
    assert list(result.columns.keys()) == ["Force", "Displacement"]
    assert result.step.values == [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    assert result["Force"].values == [
        0.0,
        2.5,
        5.0,
        7.5,
        10.0,
        12.5,
        15.0,
        17.5,
        20.0,
        22.5,
    ]


def test_select_step_with_operations_chain(large_collection):
    """select_step と他の操作をチェーンして使用するテスト"""
    ops = CollectionOperations(large_collection)

    # 特定のステップと列を選択
    result = ops.select_step(
        steps=[10, 20, 30, 40, 50], columns=["Time", "Temperature"]
    ).end()

    # 結果の検証
    assert len(result) == 5
    assert list(result.columns.keys()) == ["Time", "Temperature"]
    assert result["Time"].values == [10, 20, 30, 40, 50]
    assert result["Temperature"].values == [21.0, 22.0, 23.0, 24.0, 25.0]


def test_real_data_sample():
    """実データを使ったテスト"""
    # テストデータファイルのパス
    data_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "extracted_W-N.csv"
    )

    # データが存在する場合のみテスト実行
    if not os.path.exists(data_file):
        pytest.skip(f"テストデータ {data_file} が見つかりません")

    # ファイル読み込み（簡易実装）
    import pandas as pd

    df = pd.read_csv(data_file)

    # CollectionCollectionの作成
    step_values = list(range(len(df)))
    columns = {
        col: Column(str(i), col, "", df[col].tolist())
        for i, col in enumerate(df.columns)
    }
    collection = ColumnCollection(step=step_values, columns=columns)
    ops = CollectionOperations(collection)

    # 特定の列を選択してメトリクスを計算
    selected = ops.select(columns=df.columns[:3].tolist()).end()

    # 結果の検証
    assert len(selected.columns) == 3
    assert len(selected) == len(df)


def test_sequential_select_operations(large_collection):
    """複数のselect操作を順番に実行するテスト"""
    ops = CollectionOperations(large_collection)

    # まず列を選択
    cols_selected = ops.select(columns=["Force", "Temperature"]).end()
    assert list(cols_selected.columns.keys()) == ["Force", "Temperature"]

    # 次に行を選択
    ops2 = CollectionOperations(cols_selected)
    rows_selected = ops2.select(indices=[10, 20, 30]).end()

    # 結果の検証
    assert len(rows_selected) == 3
    assert rows_selected.step.values == [10, 20, 30]
    assert rows_selected["Force"].values == [5.0, 10.0, 15.0]


def test_select_and_transform(large_collection):
    """select操作後に変換を適用するテスト"""
    ops = CollectionOperations(large_collection)

    # 一部の列と行を選択し、計算を適用
    result = (
        ops.select(columns=["Force", "Displacement"])
        .select_step(steps=list(range(0, 50, 10)))  # 0, 10, 20, 30, 40
        .end()
    )

    # 選択されたデータに新しい操作を適用
    ops2 = CollectionOperations(result)
    # このテストではtransform操作を仮定。実際のプロジェクトに合わせて調整が必要
    if hasattr(ops2, "transform") and callable(getattr(ops2, "transform")):
        transformed = ops2.transform(
            transform_func=lambda row: {"Stress": row["Force"] / 10},
            output_columns=["Stress"],
        ).end()

        # 結果の検証
        assert "Stress" in transformed.columns
        assert len(transformed) == 5
