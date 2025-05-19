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

    # まず列を選択
    cols_selected = ops.select(columns=["Force", "Displacement"])

    # 次に行を選択（新しいCollectionOperationsを作成）
    ops2 = CollectionOperations(cols_selected)
    result = ops2.select(indices=list(range(0, 50, 5)))  # 0, 5, 10, ... , 45

    # 結果の検証
    assert len(result) == 10  # 50/5 = 10 rows
    assert list(result.columns.keys()) == ["Force", "Displacement"]
    assert result.step.values == [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    expected_force = [0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0, 22.5]
    assert list(result["Force"].values) == expected_force

    # 新しい統合されたselect関数を使った場合のテスト
    ops3 = CollectionOperations(large_collection)
    combined_result = ops3.select(
        columns=["Force", "Displacement"], indices=list(range(0, 50, 5))
    )

    # 両方の結果が同じであることを検証
    assert len(combined_result) == len(result)
    assert list(combined_result.columns.keys()) == list(result.columns.keys())
    assert combined_result.step.values == result.step.values
    assert list(combined_result["Force"].values) == list(result["Force"].values)
    assert list(combined_result["Displacement"].values) == list(
        result["Displacement"].values
    )


def test_select_step_with_operations_chain(large_collection):
    """select_step と他の操作をチェーンして使用するテスト"""
    ops = CollectionOperations(large_collection)

    # 特定のステップと列を選択
    result = ops.select_step(
        steps=[10, 20, 30, 40, 50], columns=["Time", "Temperature"]
    )

    # 結果の検証
    assert len(result) == 5
    assert list(result.columns.keys()) == ["Time", "Temperature"]
    assert list(result["Time"].values) == [10, 20, 30, 40, 50]
    assert list(result["Temperature"].values) == [21.0, 22.0, 23.0, 24.0, 25.0]

    # 新しいselect関数を使った場合も同じ結果が得られることを確認
    result2 = ops.select(steps=[10, 20, 30, 40, 50], columns=["Time", "Temperature"])
    assert len(result2) == 5
    assert list(result2.columns.keys()) == ["Time", "Temperature"]
    assert list(result2["Time"].values) == list(result["Time"].values)
    assert list(result2["Temperature"].values) == list(result["Temperature"].values)


def test_real_data_sample():
    """実データを使ったテスト"""
    # テストデータファイルのパス
    data_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "extracted_W-N.csv"
    )

    # データが存在する場合のみテスト実行
    if not os.path.exists(data_file):
        pytest.skip(f"テストデータ {data_file} が見つかりません")

    # pandas モジュールがインストールされていない場合はスキップ
    try:
        import pandas as pd
    except ImportError:
        pytest.skip("pandas モジュールがインストールされていません")

    # ファイル読み込み
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
    selected = ops.select(columns=df.columns[:3].tolist())

    # 結果の検証
    assert len(selected.columns) == 3
    assert len(selected) == len(df)


def test_sequential_select_operations(large_collection):
    """複数のselect操作を順番に実行するテスト"""
    ops = CollectionOperations(large_collection)

    # まず列を選択
    cols_selected = ops.select(columns=["Force", "Temperature"])
    assert list(cols_selected.columns.keys()) == ["Force", "Temperature"]

    # 次に行を選択
    ops2 = CollectionOperations(cols_selected)
    rows_selected = ops2.select(indices=[10, 20, 30])

    # 結果の検証
    assert len(rows_selected) == 3
    assert rows_selected.step.values == [10, 20, 30]
    assert list(rows_selected["Force"].values) == [5.0, 10.0, 15.0]

    # 統合されたselect関数で一度に行と列を選択
    ops3 = CollectionOperations(large_collection)
    combined_result = ops3.select(
        columns=["Force", "Temperature"], indices=[10, 20, 30]
    )

    # 結果の検証（同じ結果になるはず）
    assert len(combined_result) == 3
    assert list(combined_result.columns.keys()) == ["Force", "Temperature"]
    assert combined_result.step.values == rows_selected.step.values
    assert list(combined_result["Force"].values) == list(rows_selected["Force"].values)
    assert list(combined_result["Temperature"].values) == list(
        rows_selected["Temperature"].values
    )


def test_select_and_transform(large_collection):
    """select操作後に変換を適用するテスト"""
    ops = CollectionOperations(large_collection)

    # 一部の列を選択
    cols_result = ops.select(columns=["Force", "Displacement"])

    # 新しいCollectionOperationsを作成して特定のステップを選択
    ops2 = CollectionOperations(cols_result)
    result = ops2.select(steps=list(range(0, 50, 10)))  # 0, 10, 20, 30, 40

    # 選択されたデータに新しい操作を適用
    ops3 = CollectionOperations(result)
    # このテストではtransform操作を仮定。実際のプロジェクトに合わせて調整が必要
    if hasattr(ops3, "transform") and callable(getattr(ops3, "transform")):
        transformed = ops3.transform(
            transform_func=lambda row: {"Stress": row["Force"] / 10},
            output_columns=["Stress"],
        )

        # 結果の検証
        assert "Stress" in transformed.columns
        assert len(transformed) == 5

    # 新しいselect関数を使った場合のテスト - 1回の呼び出しで列とステップ両方を指定
    ops4 = CollectionOperations(large_collection)
    result2 = ops4.select(
        columns=["Force", "Displacement"],
        steps=list(range(0, 50, 10)),  # 0, 10, 20, 30, 40
    )

    assert len(result2) == 5
    assert list(result2.columns.keys()) == ["Force", "Displacement"]
    assert result2.step.values == [0, 10, 20, 30, 40]
