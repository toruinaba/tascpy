import pytest
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column
from src.tascpy.operations.core.split import split_by_integers
from src.tascpy.operations.proxy import CollectionOperations
from src.tascpy.operations.list_proxy import CollectionListOperations


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionを作成するフィクスチャ"""
    steps = [1, 2, 3, 4, 5, 6]
    columns = {
        "A": Column(ch="A", name="A値", unit="m", values=[10, 20, 30, 40, 50, 60]),
        "B": Column(
            ch="B", name="B値", unit="s", values=[1.1, 2.2, 3.3, 4.4, 5.5, 6.6]
        ),
    }
    return ColumnCollection(step=steps, columns=columns)


@pytest.fixture
def collection_list(sample_collection):
    """テスト用のCollectionListOperationsを作成するフィクスチャ"""
    # 3グループに分割
    markers = [1, 2, 1, 3, 2, 3]
    collections = split_by_integers(sample_collection, markers)
    return CollectionListOperations(collections)


def test_collection_list_len(collection_list):
    """CollectionListOperationsの__len__メソッドをテスト"""
    assert len(collection_list) == 3


def test_collection_list_getitem_index(collection_list):
    """CollectionListOperationsの__getitem__メソッド（インデックス）をテスト"""
    # インデックスでのアクセス
    item0 = collection_list[0]
    assert isinstance(item0, CollectionOperations)
    assert item0.end().step.values == [1, 3]
    assert item0.end().columns["A"].values == [10, 30]
    assert item0.end().columns["B"].values == [1.1, 3.3]

    # インデックスが範囲外の場合
    with pytest.raises(IndexError):
        collection_list[10]


def test_collection_list_getitem_slice(collection_list):
    """CollectionListOperationsの__getitem__メソッド（スライス）をテスト"""
    # スライスでのアクセス
    items = collection_list[0:2]
    assert isinstance(items, CollectionListOperations)
    assert len(items) == 2

    # 空スライス
    empty = collection_list[3:4]
    assert isinstance(empty, CollectionListOperations)
    assert len(empty) == 0


def test_collection_list_map(collection_list):
    """CollectionListOperationsのmapメソッドをテスト"""
    # filter_out_none操作を使ってテスト
    results = collection_list.map("filter_out_none")
    assert isinstance(results, CollectionListOperations)
    assert len(results) == 3

    # 存在しない操作でのマップ
    with pytest.raises(AttributeError):
        collection_list.map("non_existent_operation")


def test_collection_list_filter(collection_list):
    """CollectionListOperationsのfilterメソッドをテスト"""
    # 要素数2以上のコレクションだけをフィルタリング
    filtered = collection_list.filter(lambda col: len(col) >= 2)
    assert isinstance(filtered, CollectionListOperations)
    assert len(filtered) == 3  # 全てのコレクションが条件に合致

    # 要素数10以上のコレクションだけをフィルタリング（該当なし）
    filtered = collection_list.filter(lambda col: len(col) > 10)
    assert isinstance(filtered, CollectionListOperations)
    assert len(filtered) == 0

    # A列の平均値が30以上のコレクションだけをフィルタリング
    filtered = collection_list.filter(
        lambda col: sum(col.columns["A"].values) / len(col) > 30
    )
    assert isinstance(filtered, CollectionListOperations)
    assert len(filtered) == 2  # グループ2とグループ3が条件に合致


def test_collection_list_concat(collection_list):
    """CollectionListOperationsのconcatメソッドをテスト"""
    # 複数のコレクションを連結
    merged = collection_list.concat()
    assert isinstance(merged, CollectionOperations)

    # 結果検証
    result = merged.end()
    assert len(result) == 6  # 全データポイント数

    # マーカー1, 2, 3の順で連結されていることを確認
    assert result.step.values[0] == 1  # グループ1の最初のステップ
    assert result.step.values[2] == 2  # グループ2の最初のステップ
    assert result.step.values[4] == 4  # グループ3の最初のステップ

    # 空のコレクションリストの連結
    empty_list = CollectionListOperations([])
    with pytest.raises(ValueError):
        empty_list.concat()


def test_collection_list_end_all(collection_list):
    """CollectionListOperationsのend_allメソッドをテスト"""
    # end_allでColumnCollectionのリストを取得
    collections = collection_list.end_all()
    assert isinstance(collections, list)
    assert len(collections) == 3
    assert all(isinstance(col, ColumnCollection) for col in collections)

    # リストの内容を確認
    assert collections[0].step.values == [1, 3]
    assert collections[1].step.values == [2, 5]
    assert collections[2].step.values == [4, 6]


def test_collection_list_chaining(collection_list):
    """CollectionListOperationsのメソッドチェーンをテスト"""
    # フィルタリングしてから各コレクションに操作を適用
    results = collection_list.filter(lambda col: "A" in col.columns).map(
        "filter_out_none"
    )

    assert isinstance(results, CollectionListOperations)
    assert len(results) == 3

    # さらにフィルタリングして最初の要素を取得
    first_item = collection_list.filter(lambda col: len(col) >= 2)[0]

    assert isinstance(first_item, CollectionOperations)
    assert first_item.end().step.values == [1, 3]


def test_collection_list_with_nested_structures(collection_list):
    """CollectionListOperationsの入れ子構造の処理をテスト"""
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
        isinstance(result, CollectionListOperations) for result in nested_results
    )

    # 各サブグループの要素数を確認
    assert len(nested_results[0]) == 2  # グループ1を2つに分割
    assert len(nested_results[1]) == 2  # グループ2を2つに分割
    assert len(nested_results[2]) == 2  # グループ3を2つに分割
