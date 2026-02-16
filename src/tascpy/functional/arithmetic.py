from typing import Union, Optional, List, Any
import numpy as np

def add(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
) -> np.ndarray:
    """Add two values or arrays."""
    return np.add(v1, v2)

def subtract(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
) -> np.ndarray:
    """Subtract v2 from v1."""
    return np.subtract(v1, v2)

def multiply(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
) -> np.ndarray:
    """Multiply two values or arrays."""
    return np.multiply(v1, v2)

def divide(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
    **kwargs
) -> np.ndarray:
    """Divide v1 by v2."""
    return np.divide(v1, v2)

def diff(
    y: Union[np.ndarray, List[float]], 
    x: Union[np.ndarray, List[float]], 
    method: str = "central"
) -> np.ndarray:
    """Calculate differential coefficient from x, y coordinates."""
    # Ensure numpy arrays
    y_arr = np.asanyarray(y, dtype=float)
    x_arr = np.asanyarray(x, dtype=float)
    
    if len(x_arr) != len(y_arr):
        raise ValueError("Length of x and y must be same")
    if len(x_arr) < 2:
        raise ValueError(f"有効なデータポイントが不足しています: {len(x_arr)} (最低2点必要)")

    if method == "central":
        try:
             result = np.gradient(y_arr, x_arr)
        except Exception:
             # Fallback? Not really needed for standard gradient
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
    """Calculate integral of y with respect to x."""
    if method != "trapezoid":
        raise ValueError("現在は trapezoid 積分のみサポートしています")

    y_arr = np.asanyarray(y, dtype=float)
    x_arr = np.asanyarray(x, dtype=float)

    if len(x_arr) != len(y_arr):
        raise ValueError("Length of x and y must be same")
    if len(x_arr) < 2:
        raise ValueError(f"有効なデータポイントが不足しています: {len(x_arr)} (最低2点必要)")
        
    # Check for NaNs
    if np.isnan(y_arr).any() or np.isnan(x_arr).any():
        # Standard numpy behavior implies propagation, which is fine.
        pass

    # Sort if x is not monotonic?
    # To support integration of scattered data, we sort by x.
    # This matches original implementation behavior.
    
    # Check if sorted
    is_sorted = True
    if len(x_arr) > 1:
        if x_arr[0] < x_arr[-1]: # Simple check? No, need full check
             # If strictly increasing
             if np.any(np.diff(x_arr) < 0):
                 is_sorted = False
        else:
             # Could be decreasing or random
             is_sorted = False
             
    if not is_sorted:
        sorted_indices = np.argsort(x_arr)
        x_sorted = x_arr[sorted_indices]
        y_sorted = y_arr[sorted_indices]
    else:
        x_sorted = x_arr
        y_sorted = y_arr

    # 1. First step (0 to x[0])
    dx0 = x_sorted[0]
    first_term = dx0 * y_sorted[0]
    val0 = initial_value + first_term
    
    # 2. Subsequent steps
    dx_rest = np.diff(x_sorted)
    y_sum = y_sorted[1:] + y_sorted[:-1]
    dy_avg = y_sum / 2.0
    
    areas = dx_rest * dy_avg
    cum_areas = np.cumsum(areas)
    
    result_sorted = np.zeros(len(x_arr))
    result_sorted[0] = val0
    result_sorted[1:] = val0 + cum_areas
    
    # Unsort if needed
    if not is_sorted:
        result = np.empty_like(result_sorted)
        result[sorted_indices] = result_sorted
        return result
    else:
        return result_sorted
