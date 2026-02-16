"""
選択操作モジュール

このモジュールは選択操作（select）を提供します。
select は列名、行インデックス、ステップ値などを指定してデータを抽出する操作です。
"""

from typing import List, Optional, Dict, Any, Union, Tuple
import numpy as np
from ...core.collection import ColumnCollection
from ...core.collection import ColumnCollection
from ..registry import operation, register_functional
from ..abstraction import filter_rows, select_columns, inject_columns, inject_step_values


def _select_indices_pure(
    step_values: Union[List[Union[int, float]], np.ndarray],
    columns: Optional[List[str]] = None,
    indices: Optional[List[int]] = None,
    steps: Optional[List[Union[int, float]]] = None,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> Tuple[List[int], Dict[str, Any]]:
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
                idx = None
                if is_array:
                    # NumPy optimized search
                    if tolerance is None:
                         indices_found = np.where(step_values == target_step)[0]
                         if len(indices_found) > 0:
                             idx = int(indices_found[0])
                    else:
                         # With tolerance
                         diff = np.abs(step_values - target_step)
                         nearest_idx = np.argmin(diff)
                         if diff[nearest_idx] <= tolerance:
                             idx = int(nearest_idx)
                elif isinstance(step_values, list):
                     # List search
                     if tolerance is None:
                         try:
                              idx = step_values.index(target_step)
                         except ValueError:
                              pass
                     else:
                          for i, v in enumerate(step_values):
                              if abs(v - target_step) <= tolerance:
                                  idx = i
                                  break
                else:
                    # Generic / Numpy search fallback
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


select = register_functional(
    _select_indices_pure,
    domain="core",
    name="select",
    select_columns={"arg_name": "columns"},
    filter_rows=True,
    inject_step_values={},
    signature_override={
        # columns is handled by select_columns, but passed to pure func (ignored there but arg exists)
    }
)

def _fetch_near_step_pure(
    values: np.ndarray, value: float, **kwargs
) -> List[int]:
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


fetch_near_step = register_functional(
    _fetch_near_step_pure,
    domain="core",
    name="fetch_near_step",
    inject_columns={"num_inputs": 1},
    filter_rows=True,
)
