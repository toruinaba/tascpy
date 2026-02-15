"""
選択操作モジュール

このモジュールは選択操作（select）を提供します。
select は列名、行インデックス、ステップ値などを指定してデータを抽出する操作です。
"""

from typing import List, Optional, Dict, Any, Union, Tuple

from ...core.collection import ColumnCollection
from ..registry import operation
from ..abstraction import filter_rows, select_columns, inject_columns
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
@inject_columns(num_inputs=1)
def fetch_near_step(
    vals: Union[np.ndarray, List[float]], value: float
) -> List[int]:
    """指定された値に最も近い行を取得します

    Args:
        vals: 検索対象の列の値（@inject_columnsにより注入）
        value: 検索する値

    Returns:
        List[int]: 最も近い値を持つ行のインデックス（1つ）
    """
    # 数値型変換とチェック
    if isinstance(vals, list):
         vals = np.array(vals)
    
    if not np.issubdtype(vals.dtype, np.number):
         # Try converting to float, usually raises ValueError if strings
         try:
             vals = vals.astype(float)
         except ValueError:
             raise TypeError(f"指定された列は数値型ではありません")

    # 絶対差分
    diff = np.abs(vals - value)
    
    # 最小値のインデックスを取得
    try:
        idx = np.nanargmin(diff)
    except ValueError:
        raise ValueError("有効なデータが見つかりません")

    return [int(idx)]
