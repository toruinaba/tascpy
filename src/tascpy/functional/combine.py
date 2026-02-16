from typing import Union, Optional, List, Dict, Any, Callable
import numpy as np

# --- Helper logic moved from combine.py ---

def _switch_core(
    v1: np.ndarray,
    v2: np.ndarray,
    comp_arr: np.ndarray,
    threshold: float,
) -> np.ndarray:
    mask = comp_arr < threshold
    return np.where(mask, v1, v2)

def _blend_core(
    v1: np.ndarray,
    v2: np.ndarray,
    comp_arr: np.ndarray,
    start: float,
    end: float,
    blend_func: Callable[[float], float],
) -> np.ndarray:
    # Create masks
    mask_before = comp_arr < start
    mask_after = comp_arr > end
    mask_blend = ~mask_before & ~mask_after
    
    result = np.empty_like(v1, dtype=float) # Force float for blending
    
    # Before and After
    result[mask_before] = v1[mask_before]
    result[mask_after] = v2[mask_after]
    
    # Blend region
    if np.any(mask_blend):
        vals_blend = comp_arr[mask_blend]
        t = (vals_blend - start) / (end - start)
        
        # Apply blend func (vectorized)
        t_trans = blend_func(t)
        
        b1 = v1[mask_blend]
        b2 = v2[mask_blend]
        result[mask_blend] = b1 * (1 - t_trans) + b2 * t_trans
        
    return result

# --- Functional Operations ---

def switch_by_step(
    steps: np.ndarray,
    v1: np.ndarray,
    v2: np.ndarray,
    threshold: Union[int, float],
    compare_mode: str = "value",
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> np.ndarray:
    """Switch between v1 and v2 based on steps/index."""
    if len(v1) != len(v2):
        raise ValueError(f"列の長さが一致しません: {len(v1)} vs {len(v2)}")

    # Determine comparison array and threshold value
    if compare_mode == "value":
        comp_arr = steps if by_step_value else np.arange(len(steps))
        thresh_val = threshold
    else:  # index
        comp_arr = np.arange(len(steps))
        if by_step_value:
             # Need find_index_with_tolerance logic from utils
             # To keep functional pure and independent of complex utils if possible,
             # but here we depend on it.
             # Importing inside function or module level?
             from ...utils.searching import find_index_with_tolerance
             thresh_val = find_index_with_tolerance(
                 steps, threshold, tolerance=tolerance, default=len(steps) // 2
             )
             if thresh_val is None:
                 thresh_val = len(steps) // 2
        else:
            thresh_val = threshold

    return _switch_core(v1, v2, comp_arr, thresh_val)

def blend_by_step(
    steps: np.ndarray,
    v1: np.ndarray,
    v2: np.ndarray,
    start: Union[int, float],
    end: Union[int, float],
    compare_mode: str = "value",
    by_step_value: bool = True,
    blend_method: str = "linear",
    tolerance: Optional[float] = None,
) -> np.ndarray:
    """Blend v1 and v2 based on steps/index."""
    if len(v1) != len(v2):
        raise ValueError("列の長さが一致しません")

    # Blend functions
    blend_functions = {
        "linear": lambda t: t,
        "smooth": lambda t: 3 * t**2 - 2 * t**3,
        "log": lambda t: np.log(t * 9 + 1) / np.log(10),
        "exp": lambda t: (np.exp(t) - 1) / (np.exp(1) - 1),
    }
    if blend_method not in blend_functions:
        raise ValueError(f"無効なブレンドメソッド: {blend_method}")
        
    blend_func = np.vectorize(blend_functions[blend_method])

    # Parameter resolution
    if compare_mode == "value":
        comp_arr = steps if by_step_value else np.arange(len(steps))
        s_val, e_val = start, end
        if by_step_value and e_val <= s_val:
             raise ValueError(f"終了値({end})は開始値({start})より大きくなければなりません")
             
    else:  # index
        comp_arr = np.arange(len(steps))
        if by_step_value:
            from ...utils.searching import find_index_with_tolerance
            s_val = find_index_with_tolerance(steps, start, tolerance=tolerance, default=0)
            e_val = find_index_with_tolerance(steps, end, tolerance=tolerance, default=len(steps)-1)
        else:
            s_val, e_val = start, end
            
        if e_val <= s_val:
            raise ValueError(f"終了インデックス({e_val})は開始インデックス({s_val})より大きくなければなりません")

    return _blend_core(v1, v2, comp_arr, s_val, e_val, blend_func)

def sum_columns(arrays: List[np.ndarray]) -> np.ndarray:
    """Sum multiple arrays element-wise."""
    if not arrays:
        raise ValueError("合計対象の列が指定されていません") # Message synced with original
        
    try:
        stacked = np.stack(arrays, axis=0)
    except ValueError:
         raise ValueError("すべての列の長さが一致する必要があります")
         
    return np.sum(stacked, axis=0)

def average_columns(arrays: List[np.ndarray]) -> np.ndarray:
    """Average multiple arrays element-wise."""
    if not arrays:
        raise ValueError("平均対象の列が指定されていません")
        
    try:
        stacked = np.stack(arrays, axis=0)
    except ValueError:
         raise ValueError("すべての列の長さが一致する必要があります")

    return np.mean(stacked, axis=0)

def conditional_select(
    v1: np.ndarray,
    v2: np.ndarray,
    cond_values: np.ndarray,
    threshold: Union[int, float] = 0,
    compare: str = ">",
) -> np.ndarray:
    """Select from v1 or v2 based on condition."""
    compare_ops = {
        ">": lambda x, y: x > y,
        ">=": lambda x, y: x >= y,
        "<": lambda x, y: x < y,
        "<=": lambda x, y: x <= y,
        "==": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
    }

    if compare not in compare_ops:
        raise ValueError(
            f"無効な比較演算子: {compare}。有効なオプション: {', '.join(compare_ops.keys())}"
        )

    with np.errstate(invalid='ignore'):
         condition_mask = compare_ops[compare](cond_values, threshold)
         
         if np.issubdtype(cond_values.dtype, np.number):
             condition_mask &= ~np.isnan(cond_values)
         else:
             pass
             
    return np.where(condition_mask, v1, v2)

def custom_combine(
    v1: Any,
    v2: Any,
    combine_func: Callable[[Any, Any], Any],
    **kwargs
) -> Any:
    """Combine v1 and v2 using custom function."""
    try:
        vec_func = np.vectorize(combine_func)
        return vec_func(v1, v2)
    except:
        return [combine_func(a, b) for a, b in zip(v1, v2)]
