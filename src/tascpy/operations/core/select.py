"""
選択操作モジュール

このモジュールは選択操作（select）を提供します。
select は列名、行インデックス、ステップ値などを指定してデータを抽出する操作です。
"""

from typing import List, Optional, Dict, Any, Union, Tuple
import numpy as np
from ...core.collection import ColumnCollection
from ..registry import operation
from ..abstraction import filter_rows, select_columns, inject_columns, inject_step_values


@operation(domain="core")
@select_columns(arg_name="columns")
@filter_rows
@inject_step_values
def select(
    step_values: Union[List[Union[int, float]], np.ndarray],
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
        step_values: ステップ値のリストまたは配列 (@inject_step_valuesにより注入)
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

    # データ長
    length = len(step_values)

    # ステップ値からインデックスへの変換処理
    final_indices = indices
    found_steps = []
    missing_steps = []
    operation_type = "select"
    metadata_update = {
        "operation": "select",
        # source_columns info was here, but now implementation is decoupled.
        # select_columns decorator handles column filtering, so resultant collection reflects it.
    }

    if steps is not None:
        operation_type = "select_step"
        metadata_update["operation"] = operation_type
        final_indices = []  # stepsから変換されるインデックス

        if by_step_value:
            # ステップ値からインデックスに変換
            # step_values might be list or array
            is_array = isinstance(step_values, np.ndarray)
            
            for target_step in steps:
                # Find index logic (previously collection.step.find_step_index)
                # Re-implementing logic here using raw data to be pure
                
                idx = None
                if is_array:
                    # NumPy optimized search
                    if tolerance is None:
                         # Exact match (float comparison issues possible, use small epsilon?)
                         # Replicate logic: np.where(step_values == target_step)
                         # But Step implementation used tolerance=None -> Strict equality? 
                         # Or np.isclose?
                         # Let's assume strict if tolerance is explicitly None, unless it's float.
                         # Better to mimic `find_step_index`:
                         # if tolerance: abs(vals - val) <= tolerance
                         # else: vals == val
                         # But for float, == is risky.
                         
                         indices_found = np.where(step_values == target_step)[0]
                         if len(indices_found) > 0:
                             idx = int(indices_found[0])
                    else:
                         # With tolerance
                         diff = np.abs(step_values - target_step)
                         nearest_idx = np.argmin(diff)
                         if diff[nearest_idx] <= tolerance:
                             idx = int(nearest_idx)
                if not isinstance(step_values, np.ndarray) and isinstance(step_values, list):
                     # List search
                     found = False
                     if tolerance is None:
                         try:
                              # list.index handles exact match
                              idx = step_values.index(target_step)
                              found = True
                         except ValueError:
                              pass
                     else:
                          # Scan
                          for i, v in enumerate(step_values):
                              if abs(v - target_step) <= tolerance:
                                  idx = i
                                  found = True
                                  break
                else:
                    # Generic / Numpy search fallback for non-list iterables or just in case
                    # (Should cover the case where is_array check failed but it behaves like array)
                    # Convert to array if not
                    arr_vals = np.array(step_values) if not isinstance(step_values, np.ndarray) else step_values
                    
                    if tolerance is None:
                         indices_found = np.where(arr_vals == target_step)[0]
                         if len(indices_found) > 0:
                             idx = int(indices_found[0])
                    else:
                         diff = np.abs(arr_vals - target_step)
                         nearest_idx = np.argmin(diff)
                         if diff[nearest_idx] <= tolerance:
                             idx = int(nearest_idx)
                
                if idx is not None:
                    final_indices.append(idx)
                    found_steps.append(step_values[idx])
                else:
                    missing_steps.append(target_step)
        else:
            # 直接インデックスとして使用
            for idx in steps:
                if 0 <= idx < length:
                    final_indices.append(idx)
                    found_steps.append(step_values[idx])
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
    """指定した列名とステップ番号に基づいてデータを抽出します (後方互換性)"""
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
    values: np.ndarray, value: float, **kwargs
) -> List[int]:
    """指定された値に最も近い行を取得します
    
    inject_columnsにより、第一引数がカラム名の場合はそのカラムの値が、
    そうでない場合(数値のみ)はデフォルト(通常はStep)の値が注入されます。

    Args:
        values: 検索対象の値の配列 (@inject_columnsにより注入)
        value: 検索する値
        **kwargs: inject_columns用の追加引数

    Returns:
        List[int]: 最も近い値を持つ行のインデックス（1つ）
    """
    # 数値型変換とチェック
    if isinstance(values, list):
         values = np.array(values)
    
    if not np.issubdtype(values.dtype, np.number):
         try:
             values = values.astype(float)
         except ValueError:
             raise TypeError(f"検索対象列は数値型ではありません")

    # 絶対差分
    diff = np.abs(values - value)
    
    # NaNが含まれる場合は無視
    try:
        idx = np.nanargmin(diff)
    except ValueError:
        raise ValueError("有効なデータが見つかりません")

    return [int(idx)]
