"""
選択操作モジュール

このモジュールは選択操作（select）を提供します。
select は列名、行インデックス、ステップ値などを指定してデータを抽出する操作です。
"""

from typing import List, Optional, Dict, Any, Union, Tuple

from ...core.collection import ColumnCollection
from ..registry import operation
from ..abstraction import filter_rows, select_columns
import numpy as np


@operation(domain="core")
@select_columns(arg_name="columns")
@filter_rows
def select(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    indices: Optional[List[int]] = None,
    steps: Optional[List[Union[int, float]]] = None,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> Union[List[int], Tuple[List[int], Dict[str, Any]]]:
    """指定した列名、行インデックス、またはステップ値に基づいてデータを抽出します
    
    複数の方法でデータ抽出を行うことができる汎用的な選択操作です。
    列の選択、インデックスによる行の選択、ステップ値による行の選択を組み合わせて使用できます。

    Args:
        collection: 元の ColumnCollection
        columns: (デコレータで処理) 抽出する列名のリスト。None の場合は全列が対象
        indices: 抽出する行インデックスのリスト。None の場合は全行が対象
        steps: 抽出するステップのリスト。None の場合は全行が対象
            by_step_value=True の場合：ステップ値として解釈
            by_step_value=False の場合：インデックスとして解釈
        by_step_value: True の場合は steps をステップ値として解釈、False の場合はインデックスとして解釈
        tolerance: ステップ値検索時の許容範囲（by_step_value=True の場合のみ有効）

    Returns:
        Union[List[int], Tuple[List[int], Dict[str, Any]]]: 
            抽出する行インデックスのリスト、および更新するメタデータのタプル
    """
    # indicesとstepsの両方が指定された場合はエラー
    if indices is not None and steps is not None:
        raise ValueError("indicesとstepsは同時に指定できません")

    # ステップ値からインデックスへの変換処理
    final_indices = indices
    found_steps = []
    missing_steps = []
    operation_type = "select"
    metadata_update = {
        "operation": "select",
        "source_columns": list(collection.columns.keys()),
    }

    if steps is not None:
        operation_type = "select_step"
        metadata_update["operation"] = operation_type
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
                    
        metadata_update.update({
            "selected_steps": found_steps,
            "missing_steps": missing_steps,
            "by_step_value": by_step_value,
        })
    
    # バリデーション (indicesが直接指定された場合)
    if indices is not None:
         # インデックスの範囲チェック
         max_idx = len(collection) - 1
         min_idx = 0
         if indices:
            if max(indices) > max_idx or min(indices) < min_idx:
                 raise IndexError("指定されたインデックスが範囲外です")

    return final_indices, metadata_update


@operation(domain="core")
def select_step(
    collection: ColumnCollection,
    steps: List[Union[int, float]],
    columns: Optional[List[str]] = None,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """指定した列名とステップ番号に基づいてデータを抽出します
    
    注: この関数は後方互換性のために残されています。
    新しいコードでは select() 関数を使用することが推奨されます。
    """
    # 統合された select 関数を呼び出す
    return select(
        collection=collection,
        columns=columns,
        steps=steps,
        by_step_value=by_step_value,
        tolerance=tolerance,
    )


@operation(domain="core")
@filter_rows
def fetch_near_step(
    collection: ColumnCollection, column_name: str, value: float
) -> List[int]:
    """指定された値に最も近い行を取得します

    Args:
        collection: ColumnCollection オブジェクト
        column_name: 値を検索する列名
        value: 検索する値

    Returns:
        List[int]: 最も近い値を持つ行のインデックス（1つ）
    """
    if column_name not in collection.columns:
        raise KeyError(f"列'{column_name}'が存在しません")

    column = collection[column_name]
    vals = column.values

    # 数値型のみ対象とする
    is_numeric = False
    if isinstance(vals, np.ndarray):
        if np.issubdtype(vals.dtype, np.number):
            is_numeric = True
    elif isinstance(vals, list):
        if len(vals) > 0:
            valid_vals = [v for v in vals if v is not None]
            if valid_vals and all(isinstance(v, (int, float, np.number)) for v in valid_vals):
                is_numeric = True
                vals = np.array(vals, dtype=float)
            elif not valid_vals:
                 pass

    if not is_numeric:
        raise TypeError(f"列'{column_name}'は数値型ではありません")

    # 絶対差分
    diff = np.abs(vals - value)
    
    # 最小値のインデックスを取得
    try:
        idx = np.nanargmin(diff)
    except ValueError:
        raise ValueError("有効なデータが見つかりません")

    return [int(idx)]
