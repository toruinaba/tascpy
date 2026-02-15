import math
import numpy as np
from typing import Union, Optional, List, Dict, Any, Callable
from ...core.collection import ColumnCollection
from ...core.column import Column, detect_column_type
from ..registry import operation
from ..abstraction import transform_column


# ---------------------------------------------------------
# Naming Helpers
# ---------------------------------------------------------

def _get_col_name(args, kwargs):
    """Helper to extract column name from args or kwargs"""
    if len(args) > 0:
        return args[0]
    return kwargs.get("column")

def _basic_naming(func_name, *args, **kwargs):
    col = _get_col_name(args, kwargs)
    return f"{func_name}({col})"

def _log_naming(func_name, *args, base=math.e, **kwargs):
    col = _get_col_name(args, kwargs)
    if base == math.e:
        return f"log({col})"
    elif base == 10:
        return f"log10({col})"
    else:
        return f"log{base}({col})"

def _pow_naming(func_name, *args, exponent=1.0, **kwargs):
    col = _get_col_name(args, kwargs)
    return f"{col}^{exponent}"

def _round_naming(func_name, *args, decimals=0, **kwargs):
    col = _get_col_name(args, kwargs)
    return f"round({col}, {decimals})"

def _normalize_naming(func_name, *args, method="minmax", **kwargs):
    col = _get_col_name(args, kwargs)
    return f"norm_{method}({col})"

def _abs_naming(func_name, *args, **kwargs):
    col = _get_col_name(args, kwargs)
    return f"abs({col})"


# ---------------------------------------------------------
# Operations
# ---------------------------------------------------------
# ... (intermediate code skipped by tool logic if not modifying, but here I am modifying abs_values which is further down.
# Wait, I cannot skip huge chunks in ReplacementContent unless I use MultiReplace or close chunks.
# I will use MultiReplace to add helper and update decorator separately.


# ---------------------------------------------------------
# Operations
# ---------------------------------------------------------

# 三角関数
@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_basic_naming)
def sin(
    values: np.ndarray,
    degrees: bool = False,
    **kwargs
) -> np.ndarray:
    """指定した列の各値に sin 関数を適用します"""
    if degrees:
        values = np.radians(values)
    return np.sin(values)


@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_basic_naming)
def cos(
    values: np.ndarray,
    degrees: bool = False,
    **kwargs
) -> np.ndarray:
    """指定した列の各値に cos 関数を適用します"""
    if degrees:
        values = np.radians(values)
    return np.cos(values)


@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_basic_naming)
def tan(
    values: np.ndarray,
    degrees: bool = False,
    **kwargs
) -> np.ndarray:
    """指定した列の各値に tan 関数を適用します"""
    if degrees:
        values = np.radians(values)
    return np.tan(values)


# 指数関数/対数関数
@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_basic_naming)
def exp(
    values: np.ndarray,
    **kwargs
) -> np.ndarray:
    """指定した列の各値に指数関数(e^x)を適用します"""
    return np.exp(values)


@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_log_naming)
def log(
    values: np.ndarray,
    base: float = math.e,
    **kwargs
) -> np.ndarray:
    """指定した列の各値に対数関数を適用します"""
    # 0以下はNaNにする (元の挙動に合わせる)
    with np.errstate(divide='ignore', invalid='ignore'):
        if base == math.e:
            res_arr = np.log(values)
        elif base == 10:
            res_arr = np.log10(values)
        else:
            res_arr = np.log(values) / np.log(base)
            
    # 値が0以下の場所をNaNにする
    # values自体にNaNが含まれている可能性があるので注意
    mask_le_zero = (values <= 0)
    # maskがTrueの場所(<=0)をNaNにする
    # NaNとの比較はFalseになるので、元のNaNはそのまま
    res_arr[mask_le_zero] = np.nan
    
    return res_arr


@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_basic_naming)
def sqrt(
    values: np.ndarray,
    **kwargs
) -> np.ndarray:
    """指定した列の各値の平方根を計算します"""
    # 負の値はNaNになる (Warning抑制)
    with np.errstate(invalid='ignore'):
         return np.sqrt(values)


@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_pow_naming)
def pow(
    values: np.ndarray,
    exponent: float,
    **kwargs
) -> np.ndarray:
    """指定した列の各値を指定した指数でべき乗します"""
    with np.errstate(invalid='ignore'):
        return np.power(values, exponent)


# その他の変換関数
@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_abs_naming)
def abs_values(
    values: np.ndarray,
    **kwargs
) -> np.ndarray:
    """指定した列の各値の絶対値を計算します"""
    return np.abs(values)

# エイリアス: absはtransform.pyモジュールレベルで定義
# ただし @operation として登録するため、元の名前を使用
# 既存コードでは abs = abs_values としていた
abs = abs_values


@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_round_naming)
def round_values(
    values: np.ndarray,
    decimals: int = 0,
    **kwargs
) -> np.ndarray:
    """指定した列の各値を指定した小数点以下の桁数に丸めます"""
    return np.round(values, decimals)


@operation(domain="core")
@transform_column(num_inputs=1, result_naming=_normalize_naming)
def normalize(
    values: np.ndarray,
    method: str = "minmax",
    **kwargs
) -> np.ndarray:
    """指定した列の値を正規化します"""
    result_arr = np.full(len(values), np.nan)
    
    # 統計量計算にはNaNを除外したデータを使用
    valid_mask = ~np.isnan(values)
    if not np.any(valid_mask):
         return result_arr # All NaNs
         
    valid_arr = values[valid_mask]

    if method == "minmax":
        min_val = np.min(valid_arr)
        max_val = np.max(valid_arr)

        if max_val == min_val:
            # すべて0.5に設定 (NaN以外)
            result_arr[valid_mask] = 0.5
        else:
            result_arr = (values - min_val) / (max_val - min_val)

    elif method == "zscore":
        mean = np.mean(valid_arr)
        variance = np.var(valid_arr) # デフォルトはddof=0 (母分散)
        
        if variance < 1e-10:
             result_arr[valid_mask] = 0.0
        else:
             std_dev = np.sqrt(variance)
             result_arr = (values - mean) / std_dev
             
    else:
        raise ValueError(f"methodは['minmax', 'zscore']のいずれかを指定してください")
            
    return result_arr

