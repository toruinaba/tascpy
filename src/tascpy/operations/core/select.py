"""
選択操作モジュール

このモジュールは選択操作（select, select_step）を提供します。
select は列名および行インデックスのリストのどちらかもしくは両方を受け取って選択された対称データのみを抜き出す操作。
select_step は行インデックスではなくstep番号のリストを受け取って抜き出す操作。
"""

from typing import List, Optional, Dict, Any, Union

from tascpy.core.collection import ColumnCollection
from ..registry import operation


@operation(domain="core")
def select(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    indices: Optional[List[int]] = None,
) -> ColumnCollection:
    """指定した列名と行インデックスに基づいてデータを抽出する

    Args:
        collection: 元のColumnCollection
        columns: 抽出する列名のリスト。Noneの場合は全列が対象
        indices: 抽出する行インデックスのリスト。Noneの場合は全行が対象

    Returns:
        選択されたデータを含む新しいColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        IndexError: 指定されたインデックスが範囲外の場合
    """
    # 列の選択
    selected_columns = {}
    if columns is not None:
        # 列名の存在チェック
        for col_name in columns:
            if col_name not in collection.columns:
                raise KeyError(f"列 '{col_name}' が存在しません")

        # 選択された列のみを抽出
        selected_columns = {name: collection.columns[name].clone() for name in columns}
    else:
        # 全列をクローン
        selected_columns = {
            name: column.clone() for name, column in collection.columns.items()
        }

    # 行の選択
    selected_steps = collection.step.values
    if indices is not None:
        # インデックスの範囲チェック
        if indices and (max(indices) >= len(collection) or min(indices) < 0):
            raise IndexError("指定されたインデックスが範囲外です")

        # 選択された行のみを抽出
        selected_steps = [collection.step.values[i] for i in indices]

        # 各列の値も選択
        for name, column in selected_columns.items():
            column.values = [collection.columns[name].values[i] for i in indices]

    # 新しいCollectionを作成
    metadata = collection.metadata.copy()
    metadata.update(
        {
            "operation": "select",
            "source_columns": list(
                collection.columns.keys()
            ),  # get_id()の代わりに元のコレクションの列名リストを使用
        }
    )

    return ColumnCollection(
        step=selected_steps, columns=selected_columns, metadata=metadata
    )


@operation(domain="core")
def select_step(
    collection: ColumnCollection,
    steps: List[Union[int, float]],
    columns: Optional[List[str]] = None,
    by_step_value: bool = True,  # 追加：ステップ値を使うかインデックスを使うか
    tolerance: Optional[float] = None,  # 追加：ステップ値検索の許容範囲
) -> ColumnCollection:
    """指定した列名とステップ番号に基づいてデータを抽出する

    Args:
        collection: 元のColumnCollection
        steps: 抽出するステップ番号のリスト（by_step_value=Trueの場合）または
               インデックスのリスト（by_step_value=Falseの場合）
        columns: 抽出する列名のリスト。Noneの場合は全列が対象
        by_step_value: Trueの場合はステップ値として解釈、Falseの場合はインデックスとして解釈
        tolerance: ステップ値検索時の許容範囲（by_step_value=Trueの場合のみ有効）

    Returns:
        選択されたデータを含む新しいColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        IndexError: 指定されたインデックスが範囲外の場合
    """
    # インデックスリストを初期化
    indices = []
    found_steps = []
    missing_steps = []

    if by_step_value:
        # ステップ値からインデックスに変換
        for step in steps:
            idx = collection.step.find_step_index(step, tolerance=tolerance, default=None)
            if idx is not None:
                indices.append(idx)
                found_steps.append(collection.step.values[idx])  # 実際に見つかったステップ値を記録
            else:
                # 存在しないステップは無視して記録
                missing_steps.append(step)
    else:
        # 直接インデックスとして使用
        for idx in steps:
            if 0 <= idx < len(collection):
                indices.append(idx)
                found_steps.append(collection.step.values[idx])
            else:
                # 範囲外のインデックスは無視して記録
                missing_steps.append(idx)

    # 選択するステップがない場合は空のコレクションを返す
    if not indices:
        # 列の選択
        selected_columns = {}
        if columns is not None:
            # 列名の存在チェック
            for col_name in columns:
                if col_name not in collection.columns:
                    raise KeyError(f"列 '{col_name}' が存在しません")

            # 選択された列のみから空のコレクションを作成
            selected_columns = {
                name: collection.columns[name].__class__(
                    collection.columns[name].ch,
                    collection.columns[name].name,
                    collection.columns[name].unit,
                    [],
                )
                for name in columns
            }
        else:
            # 全列から空のコレクションを作成
            selected_columns = {
                name: column.__class__(column.ch, column.name, column.unit, [])
                for name, column in collection.columns.items()
            }

        # 新しい空のCollectionを作成
        metadata = collection.metadata.copy()
        metadata.update(
            {
                "operation": "select_step",
                "source_columns": list(collection.columns.keys()),
                "selected_steps": found_steps,
                "missing_steps": missing_steps,
                "by_step_value": by_step_value,
            }
        )

        return ColumnCollection(step=[], columns=selected_columns, metadata=metadata)

    # 選択操作を行う
    result = select(collection, columns, indices)

    # メタデータを更新
    result.metadata.update(
        {
            "operation": "select_step",
            "selected_steps": found_steps,
            "missing_steps": missing_steps,
            "by_step_value": by_step_value,
        }
    )

    return result
