from typing import Union, Optional, List, Any
import numpy as np
import math

def sin(values: np.ndarray, degrees: bool = False) -> np.ndarray:
    """Calculate sine of values."""
    if degrees:
        values = np.radians(values)
    return np.sin(values)

def cos(values: np.ndarray, degrees: bool = False) -> np.ndarray:
    """Calculate cosine of values."""
    if degrees:
        values = np.radians(values)
    return np.cos(values)

def tan(values: np.ndarray, degrees: bool = False) -> np.ndarray:
    """Calculate tangent of values."""
    if degrees:
        values = np.radians(values)
    return np.tan(values)

def exp(values: np.ndarray) -> np.ndarray:
    """Calculate exponential of values."""
    return np.exp(values)

def log(values: np.ndarray, base: float = math.e) -> np.ndarray:
    """Calculate logarithm of values."""
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
    """Calculate square root of values."""
    with np.errstate(invalid='ignore'):
         return np.sqrt(values)

def power(values: np.ndarray, exponent: float) -> np.ndarray:
    """Calculate power of values."""
    with np.errstate(invalid='ignore'):
        return np.power(values, exponent)

def abs_values(values: np.ndarray) -> np.ndarray:
    """Calculate absolute values."""
    return np.abs(values)

def round_values(values: np.ndarray, decimals: int = 0) -> np.ndarray:
    """Round values to specified decimals."""
    return np.round(values, decimals)

def normalize(values: np.ndarray, method: str = "minmax") -> np.ndarray:
    """Normalize values using specified method."""
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
