from typing import Union, Optional, List, Dict, Any, Callable
import numpy as np

# --- Helper logic moved from combine.py ---

def _switch_core(
    v1: np.ndarray,
    v2: np.ndarray,
    comp_arr: np.ndarray,
    threshold: float,
) -> np.ndarray:
    """内部用: 閾値に基づいて配列を切り替えます。

    Args:
        v1 (np.ndarray): 閾値未満の場合の値の配列。
        v2 (np.ndarray): 閾値以上の場合の値の配列。
        comp_arr (np.ndarray): 比較対象の配列。
        threshold (float): 切り替えの閾値。

    Returns:
        np.ndarray: 切り替え後の配列。
    """
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
    """内部用: 指定範囲で配列をブレンドします。

    Args:
        v1 (np.ndarray): ブレンド開始前の値の配列。
        v2 (np.ndarray): ブレンド終了後の値の配列。
        comp_arr (np.ndarray): 比較対象の配列。
        start (float): ブレンド開始値。
        end (float): ブレンド終了値。
        blend_func (Callable[[float], float]): [0, 1] 区間の補間関数。

    Returns:
        np.ndarray: ブレンド後の配列。
    """
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
    """ステップ値またはインデックスに基づいて2つの配列を切り替えます。

    Args:
        steps (np.ndarray): ステップ値の配列。
        v1 (np.ndarray): 閾値未満の場合の値の配列。
        v2 (np.ndarray): 閾値以上の場合の値の配列。
        threshold (Union[int, float]): 切り替えの閾値。
        compare_mode (str, optional): 比較モード ('value' または 'index')。デフォルトは "value"。
        by_step_value (bool, optional): ステップ値で比較するかどうか。Falseの場合はインデックスを使用。デフォルトは True。
        tolerance (float, optional): 閾値特定時の許容誤差（compare_mode='index' かつ by_step_value=True の場合に使用）。

    Returns:
        np.ndarray: 切り替え後の配列。

    Raises:
        ValueError: v1とv2の長さが異なる場合。
    """
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
    """ステップ値またはインデックスに基づいて2つの配列を指定区間でブレンドします。

    Args:
        steps (np.ndarray): ステップ値の配列。
        v1 (np.ndarray): ブレンド開始前の値の配列。
        v2 (np.ndarray): ブレンド終了後の値の配列。
        start (Union[int, float]): ブレンド開始値。
        end (Union[int, float]): ブレンド終了値。
        compare_mode (str, optional): 比較モード ('value' または 'index')。デフォルトは "value"。
        by_step_value (bool, optional): ステップ値で比較するかどうか。Falseの場合はインデックスを使用。デフォルトは True。
        blend_method (str, optional): ブレンド方法 ('linear', 'smooth', 'log', 'exp')。デフォルトは "linear"。
        tolerance (float, optional): 開始・終了値特定時の許容誤差（compare_mode='index' かつ by_step_value=True の場合に使用）。

    Returns:
        np.ndarray: ブレンド後の配列。

    Raises:
        ValueError: v1とv2の長さが異なる場合、終了値が開始値以下の場合、または無効なブレンドメソッドが指定された場合。
    """
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
    """複数の配列の要素ごとの合計を計算します。

    Args:
        arrays (List[np.ndarray]): 合計する配列のリスト。

    Returns:
        np.ndarray: 合計された配列。

    Raises:
        ValueError: 配列リストが空の場合、または配列の長さが一致しない場合。
    """
    if not arrays:
        raise ValueError("合計対象の列が指定されていません") # Message synced with original
        
    try:
        stacked = np.stack(arrays, axis=0)
    except ValueError:
         raise ValueError("すべての列の長さが一致する必要があります")
         
    return np.sum(stacked, axis=0)

def average_columns(arrays: List[np.ndarray]) -> np.ndarray:
    """複数の配列の要素ごとの平均を計算します。

    Args:
        arrays (List[np.ndarray]): 平均する配列のリスト。

    Returns:
        np.ndarray: 平均された配列。

    Raises:
        ValueError: 配列リストが空の場合、または配列の長さが一致しない場合。
    """
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
    """条件に基づいて2つの配列から値を選択します。

    cond_values が条件を満たす位置では v1 の値を、そうでない場合は v2 の値を選択します。

    Args:
        v1 (np.ndarray): 条件真の場合の値の配列。
        v2 (np.ndarray): 条件偽の場合の値の配列。
        cond_values (np.ndarray): 条件判定に使用する値の配列。
        threshold (Union[int, float], optional): 比較の閾値。デフォルトは 0。
        compare (str, optional): 比較演算子 ('>', '>=', '<', '<=', '==', '!=')。デフォルトは ">"。

    Returns:
        np.ndarray: 選択された値の配列。

    Raises:
        ValueError: 無効な比較演算子が指定された場合。
    """
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
    """カスタム関数を使用して2つの値または配列を結合します。

    Args:
        v1 (Any): 最初の値または配列。
        v2 (Any): 2番目の値または配列。
        combine_func (Callable[[Any, Any], Any]): 2つの引数を取る結合関数。
        **kwargs: 任意の追加引数（ここでは使用されません）。

    Returns:
        Any: 結合結果（配列またはリスト）。
    """
    try:
        vec_func = np.vectorize(combine_func)
        return vec_func(v1, v2)
    except:
        return [combine_func(a, b) for a, b in zip(v1, v2)]
