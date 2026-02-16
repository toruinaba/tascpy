from typing import Any, Optional, Union, List, Dict
from ...core.collection import ColumnCollection
from ...core.column import Column
from ...core.step import Step
from ..registry import operation
from ..abstraction import inject_columns, filter_rows, inject_step_values
import numpy as np


@operation(domain="core")
@filter_rows
@inject_columns(num_inputs=1, cast_to_numpy=True)
def filter_by_value(
    vals: Union[np.ndarray, List[Any]],
    value: Any,
    tolerance: Optional[float] = None,
) -> List[bool]:
    """指定された列の値が指定された値と等しい行をフィルタリングします"""
    # vals is guaranteed to be numpy array by decorator
    
    if tolerance is not None:
        # Ensure 1D array for safe iteration
        vals_flat = vals.flatten() if hasattr(vals, "flatten") else vals

        return [
            (val >= value - tolerance) and (val <= value + tolerance)
            for val in vals_flat
        ]
    else:

        # Debugging aid/Fix: Ensure 1D bool array conversion
        result = (vals == value)
        if hasattr(result, "tolist"):
             return result.tolist()
        return list(result)


@operation(domain="core")
@filter_rows
@inject_columns(columns_arg="columns", cast_to_numpy=True)
def filter_out_none(
    data: Dict[str, Union[np.ndarray, List[Any]]], 
    columns: Optional[List[str]] = None, 
    mode: str = "any"
) -> List[bool]:
    """None値およびNaN値を含む行をフィルタリングして除外します"""
    if mode not in ["any", "all"]:
        raise ValueError("モードは'any'または'all'のいずれかである必要があります")

    if not data:
        return []
    
    # データ長の取得とキーのリスト化
    keys = list(data.keys())
    length = len(data[keys[0]])
    
    # 高速化のためにバリデーション関数を事前に決定
    # (NumPyの有無判定はモジュールレベルで行うか、ここで一度だけ行う)
    try:
        import numpy as np
        has_numpy = True
    except ImportError:
        has_numpy = False

    def is_valid(val):
        """値が有効(Not None/NaN)か判定"""
        if val is None:
            return False
        # float('nan') check
        if isinstance(val, float) and val != val:
            return False
        # numpy.nan check
        if has_numpy and isinstance(val, (float, np.number)) and np.isnan(val):
            return False
        return True

    # メインループ
    result_mask = []
    
    # 行ごとの処理
    for i in range(length):
        # その行のすべての値をチェック
        # mode='any': ひとつでも無効なら除外 (すべて有効なら保持)
        # mode='all': すべて無効なら除外 (ひとつでも有効なら保持)
        
        # 行の値を抽出
        row_values = (data[k][i] for k in keys)
        
        if mode == "any":
            # keep if all are valid
            keep = all(is_valid(v) for v in row_values)
        else:
            # keep if any is valid
            keep = any(is_valid(v) for v in row_values)
            
        result_mask.append(keep)

    return result_mask


@operation(domain="core")
@filter_rows
@inject_columns(columns_arg="columns", cast_to_numpy=True)
def remove_consecutive_duplicates_across(
    data: Dict[str, Union[np.ndarray, List[Any]]], 
    columns: Optional[List[str]] = None, 
    dup_type: str = "all"
) -> List[int]:
    """複数の列間で共通の連続重複データを削除した新しい ColumnCollection オブジェクトを返します"""
    
    if dup_type not in ["all", "any"]:
        raise ValueError("dup_typeは'all'または'any'である必要があります")

    if not data:
        return []

    keys = list(data.keys())
    length = len(data[keys[0]])
    
    if length == 0:
        return []

    indices_to_keep = [0]

    # 1行目以降をチェック
    for i in range(1, length):
        # 重複判定:
        # 指定された全列の値が、前の行と同じであれば重複とみなす。
        # つまり、いずれかの列で値が変わっていれば保持する。
        # (dup_type 'all' と 'any' は従来のロジックでは同一の挙動であったため統合)
        
        has_change = False
        for k in keys:
            if data[k][i] != data[k][i-1]:
                has_change = True
                break
        
        if has_change:
            indices_to_keep.append(i)

    return indices_to_keep


@operation(domain="core")
@filter_rows
@inject_columns(num_inputs=1, cast_to_numpy=True)
def remove_outliers(
    vals: Any,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[bool]:
    """異常値を検出して除去した新しいコレクションを返します"""
    from ..core.stats import detect_outliers

    # vals is injected as numpy array (implied by cast_to_numpy=True)
    
    flags = detect_outliers(
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


@operation(domain="core")
@filter_rows
@inject_columns(num_inputs=1, cast_to_numpy=True)
def filter_by_condition(
    vals: Any, condition: callable
) -> List[bool]:
    """指定された列の値が条件を満たす行をフィルタリングします"""
    # vals is numpy array
    return [condition(val) for val in vals]


@operation(domain="core")
@filter_rows
@inject_step_values
def remove_steps(
    step_values: Union[List[Any], np.ndarray],
    steps: List[Any], 
    tolerance: Optional[float] = None
) -> List[bool]:
    """指定されたステップ値を持つ行を削除します"""
    
    current_steps = step_values if isinstance(step_values, (list, np.ndarray)) else np.array(step_values)
    steps_to_remove = set(steps)

    if tolerance is None:
        mask = [s not in steps_to_remove for s in current_steps]
    else:
        mask = []
        steps_arr = np.array(steps)
        for s in current_steps:
            is_close = np.any(np.abs(steps_arr - s) <= tolerance)
            mask.append(not is_close)

    return mask


@operation(domain="core")
def filter_val(
    collection: ColumnCollection,
    column_name: str,
    value: Any,
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """filter_by_value のエイリアス"""
    return filter_by_value(
        collection, column_name, value, tolerance=tolerance
    )


@operation(domain="core")
def filter_cond(
    collection: ColumnCollection, column_name: str, condition: callable
) -> ColumnCollection:
    """filter_by_condition のエイリアス"""
    return filter_by_condition(collection, column_name, condition)


@operation(domain="core")
def rm_outliers(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> ColumnCollection:
    """remove_outliers のエイリアス"""
    return remove_outliers(
        collection,
        column,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )
