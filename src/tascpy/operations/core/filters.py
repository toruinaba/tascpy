from typing import Any, Optional, Union, List, Dict
from ...core.collection import ColumnCollection
from ...core.column import Column
from ...core.step import Step
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
        mask = [
            (val >= value - tolerance) and (val <= value + tolerance)
            for val in column.values
        ]
    else:
        mask = [val == value for val in column.values]

    # フィルタリングされたデータを新しいColumnCollectionに格納
    filtered_data = {
        name: [col[i] for i, m in enumerate(mask) if m]
        for name, col in collection.columns.items()
    }
    filtered_step = [collection.step[i] for i, m in enumerate(mask) if m]
    return ColumnCollection(filtered_step, filtered_data, collection.metadata)


@operation(domain="core")
def filter_out_none(
    collection: ColumnCollection, columns: Optional[List[str]] = None, mode: str = "any"
) -> ColumnCollection:
    """None値を含む行をフィルタリングして除外する

    Args:
        collection: ColumnCollectionオブジェクト
        columns: フィルタリングする対象の列名リスト（デフォルトはNone、すべての列が対象）
        mode: フィルタリングモード 'any'（いずれかの列がNoneの行を除外）または
              'all'（すべての列がNoneの行を除外）

    Returns:
        フィルタリングされたColumnCollectionオブジェクト

    Raises:
        ValueError: 不正なモードが指定された場合
        KeyError: 指定された列名が存在しない場合
    """
    if mode not in ["any", "all"]:
        raise ValueError("モードは'any'または'all'のいずれかである必要があります")

    # フィルタリング対象の列を決定
    target_columns = columns if columns is not None else list(collection.columns.keys())

    # 指定された列が存在するか確認
    for col_name in target_columns:
        if col_name not in collection.columns:
            raise KeyError(f"列'{col_name}'が存在しません")

    # Noneをフィルタリングするマスクを作成
    if mode == "any":
        # いずれかの列がNoneの行を除外
        mask = [
            all(collection[col_name][i] is not None for col_name in target_columns)
            for i in range(len(collection.step))
        ]
    else:  # mode == "all"
        # すべての列がNoneの行を除外
        mask = [
            any(collection[col_name][i] is not None for col_name in target_columns)
            for i in range(len(collection.step))
        ]

    # フィルタリングされたデータを新しいColumnCollectionに格納
    filtered_data = {
        name: [col[i] for i, m in enumerate(mask) if m]
        for name, col in collection.columns.items()
    }
    filtered_step = [collection.step[i] for i, m in enumerate(mask) if m]

    return ColumnCollection(filtered_step, filtered_data, collection.metadata.copy())


@operation(domain="core")
def remove_consecutive_duplicates_across(
    collection: ColumnCollection, columns: List[str], dup_type: str = "all"
) -> ColumnCollection:
    """複数の列間で共通の連続重複データを削除した新しいColumnCollectionオブジェクトを返します。

    すべての指定された列で、連続するデータポイントが同じ値を持つ場合にのみ、
    その重複を1つだけ残して削除します。

    Args:
        collection: 処理するColumnCollectionオブジェクト
        columns: 処理対象の列名リスト
        dup_type: 重複判定のタイプ
                 'all': すべての列で値に変化がない場合に重複と判定
                 'any': 一部の列だけでも値に変化がある場合は重複と判定しない

    Returns:
        ColumnCollection: 連続する重複を削除したデータを持つ新しいColumnCollectionオブジェクト

    Raises:
        ValueError: 不正なdup_typeが指定された場合
        KeyError: 指定された列名が存在しない場合

    Examples:
        >>> # collection["A"] = [1.0, 1.0, 2.0, 2.0, 3.0, 3.0]
        >>> # collection["B"] = [10.0, 20.0, 30.0, 30.0, 40.0, 50.0]
        >>> # collection["C"] = [5, 5, 2, 2, 8, 8]
        >>> result = remove_consecutive_duplicates_across(collection, ["A", "B", "C"])
        >>> # result["A"] = [1.0, 1.0, 2.0, 3.0, 3.0]
        >>> # result["B"] = [10.0, 20.0, 30.0, 40.0, 50.0]
        >>> # result["C"] = [5, 5, 2, 8, 8]
    """
    # dup_typeのバリデーション
    if dup_type not in ["all", "any"]:
        raise ValueError("dup_typeは'all'または'any'である必要があります")

    # 指定された列が存在するか確認
    for column_name in columns:
        if column_name not in collection.columns:
            raise KeyError(f"列'{column_name}'が存在しません")

    # データの長さが0の場合は空のコレクションを返す
    if len(collection) == 0:
        return collection.clone()

    # 保持するインデックスを特定
    indices_to_keep = []

    # 最初のインデックスは常に保持
    indices_to_keep.append(0)

    # 2番目以降のインデックスをチェック
    for i in range(1, len(collection)):
        if dup_type == "all":
            # 「all」モード: すべての列で値が変化していない場合は重複とみなす
            # つまり、いずれかの列で値が変化していれば保持する
            should_keep = False
            for column_name in columns:
                if (
                    collection[column_name].values[i]
                    != collection[column_name].values[i - 1]
                ):
                    should_keep = True
                    break
            if should_keep:
                indices_to_keep.append(i)
        elif dup_type == "any":
            # 「any」モード: いずれかの列でも値が変化していれば保持する
            should_keep = False
            for column_name in columns:
                if (
                    collection[column_name].values[i]
                    != collection[column_name].values[i - 1]
                ):
                    should_keep = True
                    break
            if should_keep:
                indices_to_keep.append(i)

    # 新しいColumnCollectionを作成
    filtered_data = {}
    for name, column in collection.columns.items():
        filtered_values = [column.values[i] for i in indices_to_keep]
        new_column = column.clone()
        new_column.values = filtered_values
        filtered_data[name] = new_column

    filtered_step = [collection.step.values[i] for i in indices_to_keep]

    return ColumnCollection(
        step=filtered_step, columns=filtered_data, metadata=collection.metadata.copy()
    )
