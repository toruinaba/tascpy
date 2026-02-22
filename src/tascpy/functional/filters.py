
from typing import Any, List, Union, Optional, Dict, Callable
import numpy as np
from . import stats as functional_stats
from . import filter_utils

def remove_outliers_mask(
    vals: Any,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[bool]:
    """外れ値を除去するためのマスクを生成します。

    外れ値ではない値に対して True、外れ値に対して False を返します。

    Args:
        vals (Any): 入力値（リストまたは配列）。
        window_size (int, optional): 移動平均のウィンドウサイズ。デフォルトは 3。
        threshold (float, optional): 外れ値判定の閾値。割合による変動がこの閾値を超えると外れ値とみなされます。デフォルトは 0.5。
        edge_handling (str, optional): 境界処理の方法 ('asymmetric' など)。デフォルトは "asymmetric"。
        min_abs_value (float, optional): ゼロ除算を防ぐための最小絶対値。デフォルトは 1e-10。
        scale_factor (float, optional): 閾値をスケーリングする係数。デフォルトは 1.0。

    Returns:
        List[bool]: 保持すべき値（非外れ値）のブール値リスト。
    """
    flags = functional_stats.detect_outliers(
        vals,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )

    if hasattr(flags, "__iter__") and not isinstance(flags, str):
         return [f == 0 for f in flags]
    else:
         return [flags == 0]

def filter_by_condition(
    vals: Any, condition: callable
) -> List[bool]:
    """条件に基づいて値をフィルタリングするためのマスクを生成します。

    Args:
        vals (Any): 入力値（リストまたは配列）。
        condition (callable): 値を引数に取り、保持すべき場合に True を返す関数。

    Returns:
        List[bool]: 保持すべき値のブール値リスト。
    """
    # vals is numpy array or list
    return [condition(val) for val in vals]

def remove_steps_mask(
    step_values: Union[List[Any], np.ndarray],
    steps: List[Any], 
    tolerance: Optional[float] = None
) -> List[bool]:
    """特定のステップを除去するためのマスクを生成します。

    指定されたステップに含まれない値に対して True を返します。

    Args:
        step_values (Union[List[Any], np.ndarray]): 入力のステップ値リスト。
        steps (List[Any]): 除去するステップのリスト。
        tolerance (float, optional): ステップ一致判定の許容誤差。デフォルトは None（完全一致）。

    Returns:
        List[bool]: 保持すべきステップ（除去対象でない）のブール値リスト。
    """
    current_steps = step_values if isinstance(step_values, (list, np.ndarray)) else np.array(step_values)
    steps_to_remove = set(steps)

    if tolerance is None:
        mask = [s not in steps_to_remove for s in current_steps]
    else:
        mask = []
        steps_arr = np.array(steps)
        # Optimization: use numpy broadcasting if steps_arr is small-ish?
        # Or iterate. Original implementation iterated.
        # Let's keep iteration for simplicity/parity, or optimize?
        # Pure function can be optimized.
        
        # If both are large, this is O(N*M).
        # Vectorized:
        # diff = np.abs(current_steps[:, None] - steps_arr[None, :])
        # is_close = np.any(diff <= tolerance, axis=1)
        # mask = ~is_close
        
        if isinstance(current_steps, np.ndarray) and isinstance(steps_arr, np.ndarray) and np.issubdtype(current_steps.dtype, np.number):
             diff = np.abs(current_steps[:, None] - steps_arr[None, :])
             is_close = np.any(diff <= tolerance, axis=1)
             mask = (~is_close).tolist()
        else:
            # Fallback for non-numeric or list
            for s in current_steps:
                try:
                    is_close = np.any(np.abs(steps_arr - s) <= tolerance)
                    mask.append(not is_close)
                except Exception:
                    # In case of type error in subtraction
                    mask.append(True) # Keep?
            
    return mask

# --- 検索操作 (search.pyから統合) ---

def search_by_condition(
    data: Dict[str, Any], 
    condition_func: Callable[[Dict[str, Any]], bool]
) -> List[int]:
    """条件関数を満たす行のインデックスを検索します。

    Args:
        data (Dict[str, Any]): カラム名をキーとするデータ辞書。
        condition_func (Callable[[Dict[str, Any]], bool]): 行データ（辞書）を受け取り、boolを返す関数。

    Returns:
        List[int]: 条件を満たす行のインデックスリスト。
    """
    if not data:
        return []

    indices = []
    
    # Check length
    length = 0
    # Prefer first column's length
    for arr in data.values():
        length = len(arr)
        break
    
    col_names = list(data.keys())
    
    for i in range(length):
        row_data = {}
        for name in col_names:
            vals = data[name]
            if i < len(vals):
                 val = vals[i]
            else:
                 val = None
            row_data[name] = val

        if condition_func(row_data):
            indices.append(i)

    return indices

def search_missing_values(data: Dict[str, Any]) -> List[int]:
    """欠損値を含む行のインデックスを検索します。

    Args:
        data (Dict[str, Any]): カラム名をキーとするデータ辞書。

    Returns:
        List[int]: いずれかのカラムに欠損値を含む行のインデックスリスト。
    """
    # Keep rows where ALL columns are valid (valid_mask is True)
    # So rows with missing values are where valid_mask is False
    valid_mask = filter_utils.filter_valid_rows(data, mode="any")
    
    # Invert mask to find rows WITH missing values
    missing_mask = [not x for x in valid_mask]
    return filter_utils.where(missing_mask)

