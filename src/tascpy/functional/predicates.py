"""
Predicates for functional operations.
These functions return boolean masks (numpy arrays of bool) based on conditions.
"""

from typing import Any, Union, Optional
import numpy as np
import operator


def _to_array(values: Any) -> np.ndarray:
    """Helper to ensure input is numpy array"""
    if isinstance(values, np.ndarray):
        return values
    return np.array(values)


def eq(values: Union[np.ndarray, list], value: Any, tolerance: Optional[float] = None) -> np.ndarray:
    """
    Check if values are equal to target value.
    Supports tolerance for float comparisons.
    """
    arr = _to_array(values)
    
    if tolerance is not None:
        # Ensure array is numeric for tolerance check
        # If object array, might fail? Let's assume numeric usage for tolerance.
        return (arr >= value - tolerance) & (arr <= value + tolerance)
    else:
        # Standard equality
        # Note: np.nan == np.nan is False
        return arr == value


def neq(values: Union[np.ndarray, list], value: Any, tolerance: Optional[float] = None) -> np.ndarray:
    """
    Check if values are NOT equal to target value.
    """
    return ~eq(values, value, tolerance)


def compare(values: Union[np.ndarray, list], op_str: str, value: Any) -> np.ndarray:
    """
    Compare values using operator string.
    Supported: ">", "<", ">=", "<=", "==", "!="
    """
    arr = _to_array(values)
    
    ops = {
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
    }
    
    if op_str not in ops:
        raise ValueError(f"Invalid operator '{op_str}'. Supported: {list(ops.keys())}")
        
    op_func = ops[op_str]
    
    with np.errstate(invalid='ignore'):
        mask = op_func(arr, value)
        
        # Handle NaN behavior
        # Keep consistent with search_by_value logic:
        # NaN is generally False, except for != which is True?
        # search_by_value logic: return indices where mask is True AND not NaN.
        # But wait, search_by_value says:
        # if op_str == "!=": mask = mask & ~np.isnan(vals)
        # else: mask = mask & ~np.isnan(vals)
        # So in ALL cases, NaN implies False in the final mask for search.
        
        # However, for pure predicate, should 'nan != 5' be True?
        # In NumPy: nan != 5 is True.
        # But if we want to "filter valid rows", usually we exclude NaNs.
        # Let's return raw comparison mask here? 
        # Or follow existing logic which seems to exclude NaNs explicitly.
        
        # existing search_by_value explicitly does & ~np.isnan(vals) for all ops.
        # So let's include that safety to match "valid data matching condition".
        
        if np.issubdtype(arr.dtype, np.number):
             mask = mask & ~np.isnan(arr)
             
    return mask


def in_range(
    values: Union[np.ndarray, list], 
    min_val: Any, 
    max_val: Any, 
    inclusive: bool = True
) -> np.ndarray:
    """
    Check if values are within range [min, max].
    """
    arr = _to_array(values)
    
    if inclusive:
        min_op, max_op = operator.ge, operator.le
    else:
        min_op, max_op = operator.gt, operator.lt

    with np.errstate(invalid='ignore'):
        mask = min_op(arr, min_val) & max_op(arr, max_val)
        
        if np.issubdtype(arr.dtype, np.number):
             mask = mask & ~np.isnan(arr)
             
    return mask


def is_valid(values: Union[np.ndarray, list]) -> np.ndarray:
    """
    Check for non-missing values (not None, not NaN).
    """
    arr = _to_array(values)
    
    if np.issubdtype(arr.dtype, np.number):
        return ~np.isnan(arr)
        
    # Object array
    def _check(x):
        if x is None: return False
        if isinstance(x, float) and np.isnan(x): return False
        if isinstance(x, (np.float64, np.float32)) and np.isnan(x): return False
        return True
        
    # Vectorize is slow but safe for mixed types
    return np.vectorize(_check)(arr)
