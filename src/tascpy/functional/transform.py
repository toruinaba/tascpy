from typing import Union, Optional, List, Any
import numpy as np
import math

def sin(values: np.ndarray, degrees: bool = False) -> np.ndarray:
    """正弦(sin)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。
        degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    if degrees:
        values = np.radians(values)
    return np.sin(values)

def cos(values: np.ndarray, degrees: bool = False) -> np.ndarray:
    """余弦(cos)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。
        degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    if degrees:
        values = np.radians(values)
    return np.cos(values)

def tan(values: np.ndarray, degrees: bool = False) -> np.ndarray:
    """正接(tan)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。
        degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    if degrees:
        values = np.radians(values)
    return np.tan(values)

def exp(values: np.ndarray) -> np.ndarray:
    """指数関数(exp)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    return np.exp(values)

def log(values: np.ndarray, base: float = math.e) -> np.ndarray:
    """対数(log)を計算します。

    0以下の値はNaNになります。

    Args:
        values (np.ndarray): 入力値の配列。
        base (float, optional): 対数の底。デフォルトは e（自然対数）。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    # Ensure values are float
    values = values.astype(float)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        if base == math.e:
            res_arr = np.log(values)
        elif base == 10:
            res_arr = np.log10(values)
        else:
            res_arr = np.log(values) / np.log(base)
            
    # Mask <=0 to NaN (consistent with original implementation)
    # Note: np.log(-1) is NaN, but np.log(0) is -inf. 
    # Original explicitly set <=0 to NaN.
    mask_le_zero = (values <= 0)
    res_arr[mask_le_zero] = np.nan
    
    return res_arr

def sqrt(values: np.ndarray) -> np.ndarray:
    """平方根(sqrt)を計算します。

    負の値はNaNになります。

    Args:
        values (np.ndarray): 入力値の配列。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    with np.errstate(invalid='ignore'):
         return np.sqrt(values)

def power(values: np.ndarray, exponent: float) -> np.ndarray:
    """累乗(power)を計算します。

    Args:
        values (np.ndarray): 基数の配列。
        exponent (float): 指数。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    with np.errstate(invalid='ignore'):
        return np.power(values, exponent)

def abs_values(values: np.ndarray) -> np.ndarray:
    """絶対値(absolute value)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    return np.abs(values)

def round_values(values: np.ndarray, decimals: int = 0) -> np.ndarray:
    """値を指定された桁数で丸めます。

    Args:
        values (np.ndarray): 入力値の配列。
        decimals (int, optional): 丸める小数点以下の桁数。デフォルトは 0。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    return np.round(values, decimals)

def normalize(values: np.ndarray, method: str = "minmax") -> np.ndarray:
    """値を正規化します。

    Args:
        values (np.ndarray): 入力値の配列。
        method (str, optional): 正規化方法。
            'minmax': 最小値を0、最大値を1にスケーリング。
            'zscore': 平均を0、標準偏差を1に標準化。デフォルトは "minmax"。

    Returns:
        np.ndarray: 正規化された配列。

    Raises:
        ValueError: 指定されたメソッドが無効な場合。
    """
    values = values.astype(float)
    result_arr = np.full(len(values), np.nan)
    
    valid_mask = ~np.isnan(values)
    if not np.any(valid_mask):
         return result_arr
         
    valid_arr = values[valid_mask]

    if method == "minmax":
        min_val = np.min(valid_arr)
        max_val = np.max(valid_arr)

        if max_val == min_val:
            result_arr[valid_mask] = 0.5
        else:
            # We want result corresponding to original shape
            # values[valid_mask] -> normalized
            norm_vals = (valid_arr - min_val) / (max_val - min_val)
            result_arr[valid_mask] = norm_vals

    elif method == "zscore":
        mean = np.mean(valid_arr)
        variance = np.var(valid_arr)
        
        if variance < 1e-10:
             result_arr[valid_mask] = 0.0
        else:
             std_dev = np.sqrt(variance)
             norm_vals = (valid_arr - mean) / std_dev
             result_arr[valid_mask] = norm_vals
             
    else:
        raise ValueError(f"methodは['minmax', 'zscore']のいずれかを指定してください")
            
    return result_arr
