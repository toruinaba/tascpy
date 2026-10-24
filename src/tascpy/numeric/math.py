
import math
from typing import List, Union

import numpy as np


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
        
    Examples:
        >>> from tascpy.numeric.math import normalize
        >>> import numpy as np
        >>> normalize(np.array([0, 5, 10]), method="minmax")
        array([0. , 0.5, 1. ])
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



# --- Arithmetic Operations (from arithmetic.py) ---


def add(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
) -> np.ndarray:
    """2つの値または配列を加算します。

    Args:
        v1 (Union[np.ndarray, float]): 最初の値または配列。
        v2 (Union[np.ndarray, float]): 2番目の値または配列。

    Returns:
        np.ndarray: 加算結果。
    """
    return np.add(v1, v2)

def subtract(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
) -> np.ndarray:
    """v1 から v2 を減算します。

    Args:
        v1 (Union[np.ndarray, float]): 最初の値または配列。
        v2 (Union[np.ndarray, float]): 引く値または配列。

    Returns:
        np.ndarray: 減算結果。
    """
    return np.subtract(v1, v2)

def multiply(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
) -> np.ndarray:
    """2つの値または配列を乗算します。

    Args:
        v1 (Union[np.ndarray, float]): 最初の値または配列。
        v2 (Union[np.ndarray, float]): 2番目の値または配列。

    Returns:
        np.ndarray: 乗算結果。
    """
    return np.multiply(v1, v2)

def divide(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float],
) -> np.ndarray:
    """v1 を v2 で除算します。

    Args:
        v1 (Union[np.ndarray, float]): 分子となる値または配列。
        v2 (Union[np.ndarray, float]): 分母となる値または配列。

    Returns:
        np.ndarray: 除算結果。
    """
    return np.divide(v1, v2)

def diff(
    y: Union[np.ndarray, List[float]], 
    x: Union[np.ndarray, List[float]], 
    method: str = "central"
) -> np.ndarray:
    """x, y座標から微分係数を計算します。

    Args:
        y (Union[np.ndarray, List[float]]): y座標の配列。
        x (Union[np.ndarray, List[float]]): x座標の配列。
        method (str, optional): 微分方法 ('central', 'forward', 'backward')。デフォルトは "central"。

    Returns:
        np.ndarray: 計算された微分係数の配列。

    Raises:
        ValueError: xとyの長さが異なる場合、またはデータ点が2点未満の場合、または無効なメソッドが指定された場合。
    """
    # Ensure numpy arrays
    y_arr = np.asanyarray(y, dtype=float)
    x_arr = np.asanyarray(x, dtype=float)
    
    if len(x_arr) != len(y_arr):
        raise ValueError("Length of x and y must be same")
    if len(x_arr) < 2:
        raise ValueError(f"有効なデータポイントが不足しています: {len(x_arr)} (最低2点必要)")

    if method == "central":
        result = np.gradient(y_arr, x_arr)
             
    elif method == "forward":
        # Forward difference: (y[i+1] - y[i]) / (x[i+1] - x[i])
        dx = np.diff(x_arr)
        dy = np.diff(y_arr)
        with np.errstate(divide='ignore', invalid='ignore'):
            d = dy / dx
        # Append last element to match length
        result = np.append(d, d[-1])
        
    elif method == "backward":
        # Backward difference
        dx = np.diff(x_arr)
        dy = np.diff(y_arr)
        with np.errstate(divide='ignore', invalid='ignore'):
            d = dy / dx
        # Insert first element to match length
        result = np.insert(d, 0, d[0])
        
    else:
        raise ValueError("Invalid method. Use 'central', 'forward', or 'backward'")

    return result

def integrate(
    y: Union[np.ndarray, List[float]],
    x: Union[np.ndarray, List[float]],
    method: str = "trapezoid",
    initial_value: float = 0.0
) -> np.ndarray:
    """x に対する y の累積積分 ∫y dx を、データの並び順に沿って台形則で計算します。

    x が増減する場合（荷重-変位の往復など）も並べ替えず、経路に沿って積分します。
    先頭の値は initial_value です。

    Args:
        y (Union[np.ndarray, List[float]]): y の配列。
        x (Union[np.ndarray, List[float]]): x の配列。
        method (str, optional): 積分方法。"trapezoid"（台形則）のみ。
        initial_value (float, optional): 積分の初期値。デフォルトは 0.0。

    Returns:
        np.ndarray: 累積積分の配列（欠損を含む区間以降は NaN）。

    Raises:
        ValueError: サポートされていないメソッドの場合、x と y の長さが異なる場合、2点未満の場合。

    Examples:
        >>> import numpy as np
        >>> from tascpy.numeric.math import integrate
        >>> integrate(y=[1.0, 1.0, 1.0], x=[10.0, 11.0, 12.0])
        array([0., 1., 2.])
        >>> integrate(y=[0.0, 2.0, 2.0], x=[0.0, 1.0, 0.0])
        array([ 0.,  1., -1.])
    """
    if method != "trapezoid":
        raise ValueError("現在は trapezoid 積分のみサポートしています")

    y_arr = np.asarray(y, dtype=float)
    x_arr = np.asarray(x, dtype=float)
    if len(x_arr) != len(y_arr):
        raise ValueError("x と y の長さが一致しません")
    if len(x_arr) < 2:
        raise ValueError(f"有効なデータポイントが不足しています: {len(x_arr)} (最低2点必要)")

    areas = np.diff(x_arr) * (y_arr[1:] + y_arr[:-1]) / 2.0
    return initial_value + np.concatenate([[0.0], np.cumsum(areas)])
