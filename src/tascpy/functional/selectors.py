"""
Selectors for functional operations.
These functions return indices or values based on criteria.
"""

from typing import Any, List, Union, Optional
import numpy as np
from . import predicates


def where(mask: Union[np.ndarray, list]) -> List[int]:
    """
    Return indices where mask is True.
    """
    if isinstance(mask, list):
         mask = np.array(mask)
         
    return np.where(mask)[0].tolist()


def top_n(values: Union[np.ndarray, list], n: int, descending: bool = True) -> List[int]:
    """
    Return indices of top N values.
    Handles NaN by excluding them.
    """
    vals = np.array(values) if isinstance(values, list) else values
    
    # Exclude NaN
    if np.issubdtype(vals.dtype, np.number):
        valid_mask = ~np.isnan(vals)
    else:
        # Object array? Assuming numeric for sorting usually.
        # But let's check.
        try:
             valid_mask = ~np.isnan(vals.astype(float))
        except:
             # Fallback: assume all valid if not convertible? Or exclude None?
             valid_mask = np.ones(len(vals), dtype=bool)

    valid_indices = np.where(valid_mask)[0]
    valid_vals = vals[valid_mask]
    
    if len(valid_vals) == 0:
        return []
        
    # Sort valid values
    sorted_idx_local = np.argsort(valid_vals)
    
    if descending:
        sorted_idx_local = sorted_idx_local[::-1]
        
    # Map back to original indices
    sorted_original = valid_indices[sorted_idx_local]
    
    # Take top N
    top_indices = sorted_original[:n]
    
    # Sort indices strictly for return (as per original spec: return sorted indices)
    top_indices.sort()
    
    return top_indices.tolist()


def nearest_index(
    values: Union[np.ndarray, list], 
    target: float, 
    tolerance: Optional[float] = None
) -> Optional[int]:
    """
    Return index of value nearest to target.
    If tolerance is provided, returns None if min diff > tolerance.
    """
    vals = np.array(values) if isinstance(values, list) else values
    
    if not np.issubdtype(vals.dtype, np.number):
         try:
             vals = vals.astype(float)
         except ValueError:
             raise TypeError("Values must be numeric for nearest search")

    diff = np.abs(vals - target)
    
    # Ignore NaNs
    try:
        idx = np.nanargmin(diff)
    except ValueError:
        return None # All NaNs or empty
        
    if tolerance is not None:
        if diff[idx] > tolerance:
            return None
            
    return int(idx)


def search(values: Union[np.ndarray, list], op_str: str, value: Any) -> List[int]:
    """
    Return indices where values satisfy the operator condition.
    """
    mask = predicates.compare(values, op_str, value)
    return where(mask)


def search_range(
    values: Union[np.ndarray, list], 
    min_value: Any, 
    max_value: Any, 
    inclusive: bool = True
) -> List[int]:
    """
    Return indices where values are within range.
    """
    mask = predicates.in_range(values, min_value, max_value, inclusive)
    return where(mask)
    
    
def search_step_range(
    steps: Union[np.ndarray, list],
    min: float,
    max: float,
    inclusive: bool = True,
    tolerance: Optional[float] = None,
    by_step_value: bool = True
) -> List[int]:
    """
    Return indices where steps are within range, with optional tolerance.
    If by_step_value is False, searches within indices matching the step length.
    """
    arr = np.array(steps) if isinstance(steps, list) else steps
    
    if not by_step_value:
        # Index based filtering
        length = len(arr)
        # Use arange as the "steps" to search
        arr = np.arange(length)
        # Tolerance logic handled below using these new 'arr'
        tolerance = None 
    
    if tolerance is not None:
         # Tolerance logic
         if inclusive:
             mask = (arr >= min - tolerance) & (arr <= max + tolerance)
         else:
             mask = (arr > min + tolerance) & (arr < max - tolerance)
    else:
         # Standard range
         mask = predicates.in_range(arr, min, max, inclusive)
         
    if np.issubdtype(arr.dtype, np.number):
         mask = mask & ~np.isnan(arr)
         
    return where(mask)
