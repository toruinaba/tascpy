"""
選択操作モジュール

このモジュールは選択操作（select）を提供します。
select は列名、行インデックス、ステップ値などを指定してデータを抽出する操作です。
"""

from typing import List, Optional, Dict, Any, Union

from tascpy.core.collection import ColumnCollection
from ..registry import operation


@operation(domain="core")
def select(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    indices: Optional[List[int]] = None,
    steps: Optional[List[Union[int, float]]] = None,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """指定した列名、行インデックス、またはステップ値に基づいてデータを抽出する

    Args:
        collection: 元のColumnCollection
        columns: 抽出する列名のリスト。Noneの場合は全列が対象
        indices: 抽出する行インデックスのリスト。Noneの場合は全行が対象
        steps: 抽出するステップのリスト。Noneの場合は全行が対象
            by_step_value=Trueの場合：ステップ値として解釈
            by_step_value=Falseの場合：インデックスとして解釈
        by_step_value: Trueの場合はstepsをステップ値として解釈、Falseの場合はインデックスとして解釈
        tolerance: ステップ値検索時の許容範囲（by_step_value=Trueの場合のみ有効）

    Returns:
        選択されたデータを含む新しいColumnCollection

    Raises:
        KeyError: 指定された列名が存在しない場合
        IndexError: 明示的に指定されたindicesが範囲外の場合（stepsの場合は無視される）
        ValueError: indicesとstepsの両方が指定された場合
    """
    # indicesとstepsの両方が指定された場合はエラー
    if indices is not None and steps is not None:
        raise ValueError("indicesとstepsは同時に指定できません")

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

    # ステップ値からインデックスへの変換処理
    final_indices = indices
    found_steps = []
    missing_steps = []
    operation_type = "select"

    if steps is not None:
        operation_type = "select_step"
        final_indices = []  # stepsから変換されるインデックス

        if by_step_value:
            # ステップ値からインデックスに変換
            for step in steps:
                idx = collection.step.find_step_index(
                    step, tolerance=tolerance, default=None
                )
                if idx is not None:
                    final_indices.append(idx)
                    found_steps.append(collection.step.values[idx])
                else:
                    missing_steps.append(step)
        else:
            # 直接インデックスとして使用
            for idx in steps:
                if 0 <= idx < len(collection):
                    final_indices.append(idx)
                    found_steps.append(collection.step.values[idx])
                else:
                    missing_steps.append(idx)

    # 選択するステップがない場合は空のコレクションを作成（stepsが指定された場合のみ）
    if steps is not None and not final_indices:
        # 列の選択
        empty_columns = {}
        if columns is not None:
            # 選択された列のみから空のコレクションを作成
            empty_columns = {
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
            empty_columns = {
                name: column.__class__(column.ch, column.name, column.unit, [])
                for name, column in collection.columns.items()
            }

        # 新しい空のCollectionを作成
        metadata = collection.metadata.copy()
        metadata.update(
            {
                "operation": operation_type,
                "source_columns": list(collection.columns.keys()),
            }
        )

        # select_step用のメタデータを追加
        if operation_type == "select_step":
            metadata.update(
                {
                    "selected_steps": found_steps,
                    "missing_steps": missing_steps,
                    "by_step_value": by_step_value,
                }
            )

        return ColumnCollection(step=[], columns=empty_columns, metadata=metadata)

    # 行の選択
    if final_indices is not None:
        # インデックスの範囲チェック (select操作のときのみエラーを発生させる）
        if indices is not None and (
            max(final_indices) >= len(collection) or min(final_indices) < 0
        ):
            raise IndexError("指定されたインデックスが範囲外です")

        # 選択された行のみを抽出
        selected_steps = [collection.step.values[i] for i in final_indices]

        # 各列の値も選択
        for name, column in selected_columns.items():
            column.values = [collection.columns[name].values[i] for i in final_indices]
    else:
        # インデックスが指定されていない場合は全行を選択
        selected_steps = collection.step.values

    # 新しいCollectionを作成
    metadata = collection.metadata.copy()
    metadata.update(
        {
            "operation": operation_type,
            "source_columns": list(collection.columns.keys()),
        }
    )

    # select_step用のメタデータを追加
    if operation_type == "select_step":
        metadata.update(
            {
                "selected_steps": found_steps,
                "missing_steps": missing_steps,
                "by_step_value": by_step_value,
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
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """指定した列名とステップ番号に基づいてデータを抽出する

    注: この関数は後方互換性のために残されています。
    新しいコードでは select() 関数を使用することが推奨されます。

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
    """
    # 統合された select 関数を呼び出す
    return select(
        collection=collection,
        columns=columns,
        steps=steps,
        by_step_value=by_step_value,
        tolerance=tolerance,
    )
