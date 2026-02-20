"""
Selectors for functional operations.
These functions return indices or values based on criteria.
"""

from typing import Any, List, Union, Optional
import numpy as np
from . import predicates


def where(mask: Union[np.ndarray, list]) -> List[int]:
    """ブール値マスクに基づいてTrueの要素のインデックスを返します。

    Args:
        mask (Union[np.ndarray, list]): ブール値の配列またはリスト。

    Returns:
        List[int]: Trueの要素のインデックスリスト。
    """
    if isinstance(mask, list):
         mask = np.array(mask)
         
    return np.where(mask)[0].tolist()


def top_n(values: Union[np.ndarray, list], n: int, descending: bool = True) -> List[int]:
    """上位N個の値のインデックスを返します。

    NaNは除外されます。結果のインデックスは昇順にソートされて返されます。

    Args:
        values (Union[np.ndarray, list]): 値の配列。
        n (int): 取得する要素数。
        descending (bool, optional): 降順（大きい順）に選択するかどうか。Falseの場合は昇順（小さい順）。デフォルトは True。

    Returns:
        List[int]: 選択された要素のインデックスリスト（昇順ソート済み）。
    """
    vals = np.array(values) if isinstance(values, list) else values
    
    # Exclude NaN
    if np.issubdtype(vals.dtype, np.number):
        valid_mask = ~np.isnan(vals)
    else:
        # Object array? Assuming numeric for sorting usually.
        # But let's check.
        try:
             valid_mask = ~np.isnan(vals.astype(float))
        except:
             # Fallback: assume all valid if not convertible? Or exclude None?
             valid_mask = np.ones(len(vals), dtype=bool)

    valid_indices = np.where(valid_mask)[0]
    valid_vals = vals[valid_mask]
    
    if len(valid_vals) == 0:
        return []
        
    # Sort valid values
    sorted_idx_local = np.argsort(valid_vals)
    
    if descending:
        sorted_idx_local = sorted_idx_local[::-1]
        
    # Map back to original indices
    sorted_original = valid_indices[sorted_idx_local]
    
    # Take top N
    top_indices = sorted_original[:n]
    
    # Sort indices strictly for return (as per original spec: return sorted indices)
    top_indices.sort()
    
    return top_indices.tolist()


def nearest_index(
    values: Union[np.ndarray, list], 
    target: float, 
    tolerance: Optional[float] = None
) -> Optional[int]:
    """指定されたターゲット値に最も近い値のインデックスを返します。

    許容誤差が指定されている場合、最小差分が許容誤差を超える場合はNoneを返します。

    Args:
        values (Union[np.ndarray, list]): 検索対象の数値配列。
        target (float): ターゲット値。
        tolerance (float, optional): 許容誤差。デフォルトは None。

    Returns:
        Optional[int]: 最も近い値のインデックス。見つからない場合や条件を満たさない場合は None。

    Raises:
        TypeError: values が数値型でない場合。
    """
    vals = np.array(values) if isinstance(values, list) else values
    
    if not np.issubdtype(vals.dtype, np.number):
         try:
             vals = vals.astype(float)
         except ValueError:
             raise TypeError("Values must be numeric for nearest search")

    diff = np.abs(vals - target)
    
    # Ignore NaNs
    try:
        idx = np.nanargmin(diff)
    except ValueError:
        return None # All NaNs or empty
        
    if tolerance is not None:
        if diff[idx] > tolerance:
            return None
            
    return int(idx)


def search(values: Union[np.ndarray, list], op_str: str, value: Any) -> List[int]:
    """演算子条件を満たす値のインデックスを返します。

    Args:
        values (Union[np.ndarray, list]): 判定対象の値の配列。
        op_str (str): 比較演算子 ('>', '<', '>=', '<=', '==', '!=')。
        value (Any): 比較するターゲット値。

    Returns:
        List[int]: 条件を満たす要素のインデックスリスト。
    """
    mask = predicates.compare(values, op_str, value)
    return where(mask)


def search_range(
    values: Union[np.ndarray, list], 
    min_value: Any, 
    max_value: Any, 
    inclusive: bool = True
) -> List[int]:
    """指定された範囲内の値のインデックスを返します。

    Args:
        values (Union[np.ndarray, list]): 判定対象の値の配列。
        min_value (Any): 範囲の下限。
        max_value (Any): 範囲の上限。
        inclusive (bool, optional): 端点を含めるかどうか。Trueの場合は [min, max]、Falseの場合は (min, max)。デフォルトは True。

    Returns:
        List[int]: 範囲内の要素のインデックスリスト。
    """
    mask = predicates.in_range(values, min_value, max_value, inclusive)
    return where(mask)
    
    
def search_step_range(
    steps: Union[np.ndarray, list],
    min: float,
    max: float,
    inclusive: bool = True,
    tolerance: Optional[float] = None,
    by_step_value: bool = True
) -> List[int]:
    """ステップ値が指定された範囲内にあるインデックスを返します。

    Args:
        steps (Union[np.ndarray, list]): ステップ値の配列。
        min (float): 範囲の下限。
        max (float): 範囲の上限。
        inclusive (bool, optional): 端点を含めるかどうか。デフォルトは True。
        tolerance (float, optional): 許容誤差。デフォルトは None。
        by_step_value (bool, optional): ステップ値に基づいて検索するかどうか。Falseの場合はインデックス自体を対象とします。デフォルトは True。

    Returns:
        List[int]: 条件を満たすステップのインデックスリスト。
    """
    arr = np.array(steps) if isinstance(steps, list) else steps
    
    if not by_step_value:
        # Index based filtering
        length = len(arr)
        # Use arange as the "steps" to search
        arr = np.arange(length)
        # Tolerance logic handled below using these new 'arr'
        tolerance = None 
    
    if tolerance is not None:
         # Tolerance logic
         if inclusive:
             mask = (arr >= min - tolerance) & (arr <= max + tolerance)
         else:
             mask = (arr > min + tolerance) & (arr < max - tolerance)
    else:
         # Standard range
         mask = predicates.in_range(arr, min, max, inclusive)
         
    if np.issubdtype(arr.dtype, np.number):
         mask = mask & ~np.isnan(arr)
         
    return where(mask)
