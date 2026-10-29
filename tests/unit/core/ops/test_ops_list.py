import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.core import CoreOps, OpsList


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionを作成するフィクスチャ"""
    steps = [1, 2, 3, 4, 5, 6]
    columns = {
        "A": Column("A値", ch="A", unit="m", values=[10, 20, 30, 40, 50, 60]),
        "B": Column("B値", ch="B", unit="s", values=[1.1, 2.2, 3.3, 4.4, 5.5, 6.6]
        ),
    }
    return ColumnCollection(columns, step=steps)


@pytest.fixture
def collection_list(sample_collection):
    """テスト用のOpsListを作成するフィクスチャ"""
    # 3グループに分割
    markers = [1, 2, 1, 3, 2, 3]
    return sample_collection.ops.split_by_integers(markers)


def test_collection_list_len(collection_list):
    """OpsListの__len__メソッドをテスト"""
    assert len(collection_list) == 3


def test_collection_list_getitem_index(collection_list):
    """OpsListの__getitem__メソッド（インデックス）をテスト"""
    # インデックスでのアクセス
    item0 = collection_list[0]
    assert isinstance(item0, CoreOps)
    np.testing.assert_array_equal(item0.end().step, [1, 3])
    np.testing.assert_array_equal(item0.end()["A"].values, [10, 30])
    np.testing.assert_allclose(item0.end()["B"].values, [1.1, 3.3])

    # インデックスが範囲外の場合
    with pytest.raises(IndexError):
        collection_list[10]


def test_collection_list_getitem_slice(collection_list):
    """OpsListの__getitem__メソッド（スライス）をテスト"""
    # スライスでのアクセス
    items = collection_list[0:2]
    assert isinstance(items, OpsList)
    assert len(items) == 2

    # 空スライス
    empty = collection_list[3:4]
    assert isinstance(empty, OpsList)
    assert len(empty) == 0


def test_collection_list_map(collection_list):
    """OpsListのmapメソッドをテスト"""
    results = collection_list.map(lambda o: o.multiply("A", 2, result_column="A2"))
    assert isinstance(results, OpsList)
    assert len(results) == 3
    np.testing.assert_array_equal(results[0].end()["A2"].values, [20, 60])
    # 元のリストは変更されない
    assert "A2" not in collection_list[0].end().columns


def test_collection_list_collect(collection_list):
    """OpsListのcollectメソッドをテスト"""
    maxima = collection_list.collect(lambda o: o.end()["A"].max())
    assert maxima == [30, 50, 60]


def test_collection_list_filter(collection_list):
    """OpsListのfilterメソッドをテスト"""
    # 要素数2以上のコレクションだけをフィルタリング
    filtered = collection_list.filter(lambda col: len(col) >= 2)
    assert isinstance(filtered, OpsList)
    assert len(filtered) == 3  # 全てのコレクションが条件に合致

    # 要素数10以上のコレクションだけをフィルタリング（該当なし）
    filtered = collection_list.filter(lambda col: len(col) > 10)
    assert isinstance(filtered, OpsList)
    assert len(filtered) == 0

    # A列の平均値が30以上のコレクションだけをフィルタリング
    filtered = collection_list.filter(
        lambda col: sum(col["A"].values) / len(col) > 30
    )
    assert isinstance(filtered, OpsList)
    assert len(filtered) == 2  # グループ2とグループ3が条件に合致


def test_collection_list_concat(collection_list):
    """OpsListのconcatメソッドをテスト"""
    # 複数のコレクションを連結
    merged = collection_list.concat()
    assert isinstance(merged, CoreOps)

    # 結果検証
    result = merged.end()
    assert len(result) == 6  # 全データポイント数

    # マーカー1, 2, 3の順で連結されていることを確認
    assert result.step[0] == 1  # グループ1の最初のステップ
    assert result.step[2] == 2  # グループ2の最初のステップ
    assert result.step[4] == 4  # グループ3の最初のステップ

    # 単位は連結後も保持される
    assert result.units == {"A": "m", "B": "s"}

    # 空のコレクションリストの連結
    empty_list = OpsList([])
    with pytest.raises(ValueError):
        empty_list.concat()


def test_collection_list_end(collection_list):
    """OpsListのendメソッドをテスト"""
    # endでColumnCollectionのリストを取得
    collections = collection_list.end()
    assert isinstance(collections, list)
    assert len(collections) == 3
    assert all(isinstance(col, ColumnCollection) for col in collections)

    # リストの内容を確認
    np.testing.assert_array_equal(collections[0].step, [1, 3])
    np.testing.assert_array_equal(collections[1].step, [2, 5])
    np.testing.assert_array_equal(collections[2].step, [4, 6])


def test_collection_list_chaining(collection_list):
    """OpsListのメソッドチェーンをテスト"""
    # フィルタリングしてから各コレクションに操作を適用
    results = collection_list.filter(lambda col: "A" in col.columns).map(
        lambda o: o.filter_out_none()
    )

    assert isinstance(results, OpsList)
    assert len(results) == 3

    # さらにフィルタリングして最初の要素を取得
    first_item = collection_list.filter(lambda col: len(col) >= 2)[0]

    assert isinstance(first_item, CoreOps)
    np.testing.assert_array_equal(first_item.end().step, [1, 3])


def test_collection_list_with_nested_structures(collection_list):
    """OpsListの入れ子構造の処理をテスト"""
    # 各コレクションをさらに分割する操作
    nested_results = []
    for i in range(len(collection_list)):
        col_op = collection_list[i]
        collection = col_op.end()
        # 各コレクションを2つに分割
        if len(collection) >= 2:
            markers = [1] * (len(collection) // 2) + [2] * (
                len(collection) - len(collection) // 2
            )
            sub_results = col_op.split_by_integers(markers)
            nested_results.append(sub_results)

    # 結果を確認
    assert len(nested_results) == 3
    assert all(
        isinstance(result, OpsList) for result in nested_results
    )

    # 各サブグループの要素数を確認
    assert len(nested_results[0]) == 2  # グループ1を2つに分割
    assert len(nested_results[1]) == 2  # グループ2を2つに分割
    assert len(nested_results[2]) == 2  # グループ3を2つに分割


def test_split_keys_follow_map_filter_and_slice(collection_list, sample_collection):
    assert collection_list.keys == [1, 2, 3]
    assert collection_list.map(lambda o: o.add("A", 1, result_column="A1")).keys == [1, 2, 3]
    assert collection_list.filter(lambda c: c["A"].values[0] > 10).keys == [2, 3]
    assert collection_list[1:].keys == [2, 3]
    assert sample_collection.ops.split_at_indices([2, 4]).keys == [0, 1, 2]


def test_to_table_rows_are_split_keys(collection_list):
    table = collection_list.to_table(max_a=lambda o: o.end()["A"].max(), rows=lambda o: len(o.end())).end()
    assert table.step.tolist() == [1, 2, 3]
    np.testing.assert_allclose(table["max_a"].values, [30, 50, 60])
    np.testing.assert_allclose(table["rows"].values, [2, 2, 2])
    assert table.units == {"max_a": None, "rows": None}


def test_to_table_expands_results_with_units(collection_list):
    from tascpy.core.result import PointResult, ScalarResult

    table = collection_list.to_table(
        mean=lambda o: ScalarResult("mean", float(o.end()["A"].values.mean()), unit="m"),
        peak=lambda o: PointResult("peak", 1.0, float(o.end()["A"].max()), x_unit="s", y_unit="m"),
    ).end()
    assert table.columns == ["mean", "peak_x", "peak_y"]
    assert table.units == {"mean": "m", "peak_x": "s", "peak_y": "m"}
    np.testing.assert_allclose(table["peak_y"].values, [30, 50, 60])


def test_to_table_rejects_unsupported_values(collection_list):
    with pytest.raises(TypeError, match="to_table"):
        collection_list.to_table(rows=lambda o: o.end())
    with pytest.raises(ValueError, match="集約する列"):
        collection_list.to_table()
