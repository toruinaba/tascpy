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


def test_split_by_integers_basic(sample_collection):
    """split_by_integersの基本機能をテスト"""
    # 3つのグループに分割
    markers = [1, 2, 1, 3, 2, 3]  # 1=グループ1, 2=グループ2, 3=グループ3
    result = split_by_integers(sample_collection, markers)

    # 結果検証
    assert len(result) == 3  # 3つのグループができているか

    # グループ1 (marker=1) の検証
    assert result[0].step.values == [1, 3]
    assert result[0].columns["A"].values == [10, 30]
    assert result[0].columns["B"].values == [1.1, 3.3]

    # グループ2 (marker=2) の検証
    assert result[1].step.values == [2, 5]
    assert result[1].columns["A"].values == [20, 50]
    assert result[1].columns["B"].values == [2.2, 5.5]

    # グループ3 (marker=3) の検証
    assert result[2].step.values == [4, 6]
    assert result[2].columns["A"].values == [40, 60]
    assert result[2].columns["B"].values == [4.4, 6.6]


def test_split_by_integers_single_marker(sample_collection):
    """単一マーカー値での分割をテスト"""
    # すべて同じマーカー値で分割
    markers = [1, 1, 1, 1, 1, 1]
    result = split_by_integers(sample_collection, markers)

    # 結果検証
    assert len(result) == 1  # 1つのグループができる
    assert result[0].step.values == [1, 2, 3, 4, 5, 6]  # 元のステップと同じ
    assert result[0].columns["A"].values == [10, 20, 30, 40, 50, 60]  # 元の値と同じ
    assert result[0].columns["B"].values == [
        1.1,
        2.2,
        3.3,
        4.4,
        5.5,
        6.6,
    ]  # 元の値と同じ


def test_split_by_integers_preserves_metadata(sample_collection):
    """メタデータが保持されることを確認するテスト"""
    # メタデータの追加
    sample_collection.metadata = {"source": "test", "date": "2025-05-03"}

    # 分割実行
    markers = [1, 2, 1, 2, 1, 2]
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
    markers = [1, 2, 1, 3, 2, 3]
    result = sample_collection.ops.split_by_integers(markers)

    # 結果がCollectionListOperationsであることを確認
    assert isinstance(result, CollectionListOperations)
    assert len(result) == 3

    # 個々のコレクションにアクセス
    first_group = result[0]
    assert isinstance(first_group, CollectionOperations)
    assert first_group.end().step.values == [1, 3]
    assert first_group.end().columns["A"].values == [10, 30]

    # スライスでのアクセスをテスト
    first_two = result[:2]
    assert isinstance(first_two, CollectionListOperations)
    assert len(first_two) == 2


def test_split_by_integers_and_method_chain(sample_collection):
    """メソッドチェーンでの操作をテスト"""
    # 分割した結果に対してフィルタリング操作を適用
    markers = [1, 2, 3, 1, 2, 3]

    # 最初の要素だけを取得（インデックス付きアクセス）
    first_group = sample_collection.ops.split_by_integers(markers)[0]
    assert isinstance(first_group, CollectionOperations)

    # 分割した結果に個別にアクセスして操作
    result = sample_collection.ops.split_by_integers(markers)

    # 個々のグループに対して操作
    group1 = result[0].end()
    assert len(group1) == 2  # マーカー1は2つある
    assert group1.step.values == [1, 4]

    group2 = result[1].end()
    assert len(group2) == 2  # マーカー2は2つある
    assert group2.step.values == [2, 5]

    group3 = result[2].end()
    assert len(group3) == 2  # マーカー3は2つある
    assert group3.step.values == [3, 6]
