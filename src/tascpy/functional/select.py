
from typing import List, Optional, Dict, Any, Union, Tuple
import numpy as np

def select_indices(
    step_values: Union[List[Union[int, float]], np.ndarray],
    columns: Optional[List[str]] = None,
    indices: Optional[List[int]] = None,
    steps: Optional[List[Union[int, float]]] = None,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> Tuple[List[int], Dict[str, Any]]:
    """
    Select indices based on steps or direct indices.
    Returns: (final_indices, metadata_update)
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
    metadata_update = {
        "operation": "select",
    }

    if steps is not None:
        metadata_update["operation"] = "select_step"
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
                         # With tolerance
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
                    # Note: Original code accessed step_values[idx] here, assume it's safe if 0<=idx<length
                    try:
                        found_steps.append(step_values[idx])
                    except IndexError:
                         pass # Should be covered by length check but just in case
                else:
                    missing_steps.append(idx)
                    
        metadata_update.update({
            "selected_steps": found_steps,
            "missing_steps": missing_steps,
            "by_step_value": by_step_value,
        })
    
    return final_indices, metadata_update

def fetch_near_step(
    values: np.ndarray, value: float, **kwargs
) -> List[int]:
    """
    Find index of nearest value.
    Returns list containing single index.
    """
    # 数値型変換とチェック
    # Handle list input if necessary (though type hint says ndarray)
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
