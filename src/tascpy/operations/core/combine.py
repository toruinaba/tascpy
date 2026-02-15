"""Columnの合成操作

このモジュールでは、2つのColumnを合成するための操作関数を提供します。
特に、ステップやインデックスを基準にした条件付き合成やブレンド操作に焦点を当てています。
"""

from typing import Union, Optional, List, Dict, Any, Callable, Tuple
import numpy as np
from ...core.collection import ColumnCollection
from ...core.column import Column, NumberColumn, detect_column_type
from ..registry import operation
from ..abstraction import inject_columns, store_result


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

@operation(domain="core")
@inject_columns(num_inputs=2, include_step=True, cast_to_numpy=True)
@store_result
def switch_by_step(
    steps: np.ndarray,
    v1: np.ndarray,
    v2: np.ndarray,
    threshold: Union[int, float],
    compare_mode: str = "value",
    by_step_value: bool = True,
    result_column: Optional[str] = None,
    in_place: bool = False,
    tolerance: Optional[float] = None,
) -> Any:
    """ステップ値を基準に2つのColumnを切り替える (ベクトル化済み)"""
    if len(v1) != len(v2):
        raise ValueError(f"列の長さが一致しません: {len(v1)} vs {len(v2)}")

    # 比較配列の決定
    if compare_mode == "value":
        comp_arr = steps if by_step_value else np.arange(len(steps))
        thresh_val = threshold
    else:  # index
        comp_arr = np.arange(len(steps))
        if by_step_value:
             from tascpy.utils.searching import find_index_with_tolerance
             thresh_val = find_index_with_tolerance(
                 steps, threshold, tolerance=tolerance, default=len(steps) // 2
             )
             if thresh_val is None:
                 thresh_val = len(steps) // 2
        else:
            thresh_val = threshold

    new_values = _switch_core(v1, v2, comp_arr, thresh_val)

    metadata = {
            "operation": "switch_by_step",
            "by_step_value": by_step_value,
            "compare_mode": compare_mode,
            "threshold": threshold,
    }
    return new_values, metadata


@operation(domain="core")
@inject_columns(num_inputs=2, include_step=True, cast_to_numpy=True)
@store_result
def blend_by_step(
    steps: np.ndarray,
    v1: np.ndarray,
    v2: np.ndarray,
    start: Union[int, float],
    end: Union[int, float],
    compare_mode: str = "value",
    by_step_value: bool = True,
    blend_method: str = "linear",
    result_column: Optional[str] = None,
    in_place: bool = False,
    tolerance: Optional[float] = None,
) -> Any:
    """ステップ値の範囲内で2つのColumnをブレンドする (ベクトル化済み)"""
    if len(v1) != len(v2):
        raise ValueError("列の長さが一致しません")

    # ブレンド関数
    blend_functions = {
        "linear": lambda t: t,
        "smooth": lambda t: 3 * t**2 - 2 * t**3,
        "log": lambda t: np.log(t * 9 + 1) / np.log(10),
        "exp": lambda t: (np.exp(t) - 1) / (np.exp(1) - 1),
    }
    if blend_method not in blend_functions:
        raise ValueError(f"無効なブレンドメソッド: {blend_method}")
        
    blend_func = np.vectorize(blend_functions[blend_method]) # Vectorize for usage on array

    # パラメータ解決
    if compare_mode == "value":
        comp_arr = steps if by_step_value else np.arange(len(steps))
        s_val, e_val = start, end
        if by_step_value and e_val <= s_val:
             raise ValueError(f"終了値({end})は開始値({start})より大きくなければなりません")
             
    else:  # index
        comp_arr = np.arange(len(steps))
        if by_step_value:
            from tascpy.utils.searching import find_index_with_tolerance
            s_val = find_index_with_tolerance(steps, start, tolerance=tolerance, default=0)
            e_val = find_index_with_tolerance(steps, end, tolerance=tolerance, default=len(steps)-1)
            
            # Defaults handled by utils default logic (passed above)
        else:
            s_val, e_val = start, end
            
        if e_val <= s_val:
            raise ValueError(f"終了インデックス({e_val})は開始インデックス({s_val})より大きくなければなりません")

    new_values = _blend_core(v1, v2, comp_arr, s_val, e_val, blend_func)

    metadata = {
            "operation": "blend_by_step",
            "by_step_value": by_step_value,
            "compare_mode": compare_mode,
            "start": start,
            "end": end,
            "blend_method": blend_method,
    }
    return new_values, metadata


@operation(domain="core")
@inject_columns(columns_arg="columns", cast_to_numpy=True)
@store_result
def sum_columns(
    data: Dict[str, np.ndarray],
    columns: Optional[List[str]] = None,
) -> Any:
    """複数の列を合計します。
    
    指定した複数の列の値を要素ごとに合計し、結果の配列を返します。
    
    Args:
        data: 列データの辞書 (inject_columnsにより注入)
        columns: 合計対象の列名リスト
    """
    if not data:
        raise ValueError("合計対象の列が指定されていません")
        
    # Check lengths (implicit in inject_columns usually, but safe to check if dict has varying lengths?)
    # inject_columns extracts from same collection, so lengths are same.
    
    # Calculate sum
    # Create stacked array
    try:
        stacked = np.stack(list(data.values()), axis=0)
    except ValueError:
         # Different lengths?
         raise ValueError("すべての列の長さが一致する必要があります")
         
    return np.sum(stacked, axis=0)


@operation(domain="core")
@inject_columns(columns_arg="columns", cast_to_numpy=True)
@store_result
def average_columns(
    data: Dict[str, np.ndarray],
    columns: Optional[List[str]] = None,
) -> Any:
    """複数の列の平均値を計算します。
    
    指定した複数の列の値を要素ごとに平均し、結果の配列を返します。
    
    Args:
        data: 列データの辞書 (inject_columnsにより注入)
        columns: 平均対象の列名リスト
    """
    if not data:
        raise ValueError("平均対象の列が指定されていません")
        
    try:
        stacked = np.stack(list(data.values()), axis=0)
    except ValueError:
         raise ValueError("すべての列の長さが一致する必要があります")

    return np.mean(stacked, axis=0)


@operation(domain="core")
@inject_columns(num_inputs=3, cast_to_numpy=True)
@store_result
def conditional_select(
    v1: np.ndarray,
    v2: np.ndarray,
    cond_values: np.ndarray,
    threshold: Union[int, float] = 0,
    compare: str = ">",
) -> Any:
    """条件に基づいて2つの値を選択的に取得します
    
    Args:
        v1: 条件を満たす場合に使用する値
        v2: 条件を満たさない場合に使用する値
        cond_values: 条件判定に使用する値
        threshold: 条件判定の閾値
        compare: 比較演算子
    """
    # 入力検証 (Length check is done by numpy broadcasting usually, but safe to check equality?)
    # inject_columns ensures arrays.
    
    # 比較演算子の検証と関数マッピング
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

    # 比較実行 (Vectorized)
    # Check for NaN/None in cond_values?
    # Original logic: if cond_values[i] is not None and compare(...)
    # NumPy comparison involving NaN:
    # > : False (usually)
    # So we need to handle None/NaN explicitly if we want exact same behavior.
    
    # Cast to float array if object (done by cast_to_numpy=True if mostly numbers)
    # But if it contains None, it might be object array or float with nan.
    
    with np.errstate(invalid='ignore'):
         condition_mask = compare_ops[compare](cond_values, threshold)
         
         # Handle NaN/None -> False (Treat as not meeting condition, enabling v2)
         if np.issubdtype(cond_values.dtype, np.number):
             condition_mask &= ~np.isnan(cond_values)
         else:
             # Object array fallback?
             pass # cast_to_numpy attempts float conversion, so likely float array.
             
    return np.where(condition_mask, v1, v2)


@operation(domain="core")
@inject_columns(num_inputs=2, cast_to_numpy=True)
@store_result
def custom_combine(
    v1: Any,
    v2: Any,
    combine_func: Callable[[Any, Any], Any],
    func_name: Optional[str] = None,
) -> Any:
    """カスタム関数を使用して2つの値を合成します"""
    
    # Vectorize the function? 
    # Or list comprehension if it's complex Python object?
    # Original logic handles None explicitly.
    
    # If arrays are number, vectorized might fail if func expects python scalars or None.
    # To be safe and support generic functions, let's use list comprehension or np.vectorize
    
    # But optimal is np.vectorize if simpler.
    # Let's use list comprehension for maximum compatibility with arbitrary user functions
    # including None handling.
    
    # But cast_to_numpy=True converts None to NaN for floats.
    # If custom func handles None, it receives NaN now.
    
    # If user wants None, maybe we should NOT cast to numpy for this flexible function?
    # But plan said "pure function". 
    # Let's try vectorized approach first.
    
    # If v1, v2 are arrays:
    try:
        # Note: combine_func might not support vectorization.
        # Use np.vectorize
        vec_func = np.vectorize(combine_func)
        return vec_func(v1, v2)
    except:
        # Fallback to list comprehension zip
        # This preserves strict types?
        return [combine_func(a, b) for a, b in zip(v1, v2)]
