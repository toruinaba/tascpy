from typing import Any, List, Dict, Optional, Union
from ...core.collection import ColumnCollection
from ...core.column import Column
from ..registry import operation


@operation(domain="core")
def split_by_integers(
    collection: ColumnCollection, markers: List[int]
) -> List[ColumnCollection]:
    """
    整数リストの値でデータを分割します。同じマーカー値を持つデータは同じグループに集約されます。

    Args:
        collection: 分割するColumnCollectionオブジェクト
        markers: 各データ値がどのグループに属するかを示す整数リスト（データと同じ長さ）

    Returns:
        分割後のColumnCollectionオブジェクトのリスト。各ColumnCollectionは同じマーカー値を持つ
        データで構成され、マーカー値に基づいて昇順に並べられます。

    Raises:
        ValueError: データとマーカーの長さが一致しない場合

    Examples:
        # データ値を3つのグループに分類
        markers = [2, 1, 2, 3, 1, 3]  # マーカー値が示す分類グループ
        collection_groups = split_by_integers(collection, markers)
        # 結果: [グループ1のCollection, グループ2のCollection, グループ3のCollection]
    """
    from ...utils.split import split_list_by_integers

    if len(collection.step.values) != len(markers):
        raise ValueError(
            f"{len(collection.step.values)}vs{len(markers)}:データリストとマーカーリストの長さは一致する必要があります."
        )

    # マーカー値のユニークな集合を取得（ソートして）
    unique_markers = sorted(set(markers))

    # 各マーカー値ごとにCollectionを作成
    result_collections = []

    for marker in unique_markers:
        # このマーカーに対応するステップのインデックスを取得
        indices = [i for i, m in enumerate(markers) if m == marker]

        # 新しいコレクションのデータを準備
        new_steps = [collection.step.values[i] for i in indices]
        new_columns = {}

        # 各カラムのデータを抽出
        for name, column in collection.columns.items():
            new_values = [column.values[i] for i in indices]

            # 新しいカラムを作成
            new_column = column.clone()
            new_column.values = new_values
            new_columns[name] = new_column

        # 新しいCollectionを作成して結果に追加
        new_collection = ColumnCollection(
            step=new_steps, columns=new_columns, metadata=collection.metadata.copy()
        )

        result_collections.append(new_collection)

    return result_collections
