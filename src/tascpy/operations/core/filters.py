from typing import Any, Optional, Union, List, Dict
from ...core.collection import ColumnCollection
from ...core.column import Column
from ...core.indices import Indices
from ..registry import operation


@operation(domain="core")
def filter_by_value(
    collection: ColumnCollection,
    column_name: str,
    value: Any,
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """指定された列の値が指定された値と等しい行をフィルタリング
    Args:
        collection: ColumnCollectionオブジェクト
        column_name: フィルタリングする列の名前
        value: フィルタリングする値
        tolerance: 値の許容範囲（デフォルトはNone）
    Returns:
        フィルタリングされたColumnCollectionオブジェクト
    Raises:
        KeyError: 指定された列名が存在しない場合
        TypeError: 指定された列がColumnオブジェクトでない場合
    """
    if column_name not in collection.columns:
        raise KeyError(f"列'{column_name}'が存在しません")

    column = collection[column_name]
    if not isinstance(column, Column):
        raise TypeError(f"'{column_name}'はColumnオブジェクトではありません")

    # 値のフィルタリング
    if tolerance is not None:
        mask = (column.values >= value - tolerance) & (
            column.values <= value + tolerance
        )
    else:
        mask = column.values == value

    # フィルタリングされたデータを新しいColumnCollectionに格納
    filtered_data = {name: col[mask] for name, col in collection.columns.items()}
    return ColumnCollection(collection.step[mask], filtered_data, collection.metadata)
