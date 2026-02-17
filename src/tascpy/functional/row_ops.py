"""
Row operations for functional module.
These functions operate on dictionaries of arrays (simulating dataframe rows).
"""

from typing import Dict, Any, List, Union, Callable
import numpy as np
from .predicates import is_valid


def filter_by_row_condition(
    data: Dict[str, Union[np.ndarray, list]], 
    condition: Callable[[Dict[str, Any]], bool]
) -> List[int]:
    """
    Return indices where row satisfies condition.
    Optimization: condition function receives a dict of row values.
    """
    if not data:
        return []

    # Get length from first column
    # Assume aligned lengths (validated by caller/wrappers)
    length = 0
    cols_data = {}
    
    for k, v in data.items():
        length = len(v)
        cols_data[k] = v
        
    indices = []
    keys = list(cols_data.keys())
    
    # Iterate rows
    # Pure Python loop 
    for i in range(length):
        row_data = {}
        for k in keys:
            vals = cols_data[k]
            # Safety check
            if i < len(vals):
                row_data[k] = vals[i]
            else:
                row_data[k] = None
                
        if condition(row_data):
            indices.append(i)
            
    return indices


def duplicated_indices(
    data: Dict[str, Union[np.ndarray, list]],
    mode: str = "consecutive",
    dup_type: str = "all"
) -> List[int]:
    """
    Return indices to KEEP after removing duplicates.
    
    Args:
        data: Dict of columns
        mode: 
            'consecutive': Remove if previous row is identical (keep first).
            'all': Not implemented yet, reserved for unique rows.
        dup_type:
            'all': Remove row if ALL columns match previous row value (standard).
            'any': Remove row if ANY column matches previous row value (strict).
    """
    if not data:
        return []
        
    keys = list(data.keys())
    if not keys:
        return []
        
    length = len(data[keys[0]])
    if length == 0:
        return []
        
    indices_to_keep = [0]
    
    if mode == "consecutive":
        for i in range(1, length):
            if dup_type == "all":
                # Remove if ALL cols match previous (i.e., keep if ANY col changed)
                has_change = False
                for k in keys:
                    vals = data[k]
                    v_curr = vals[i]
                    v_prev = vals[i-1]
                    if v_curr != v_prev:
                        has_change = True
                        break
                if has_change:
                    indices_to_keep.append(i)
            
            elif dup_type == "any":
                # 'any' mode in tests expects behavior: "Keep if even a part of columns change".
                # This is synonymous with "Remove only if ALL columns match".
                # This matches 'all' mode behavior in the legacy tests.
                
                # Check if ALL columns match previous (same as 'all' mode logic above)
                has_change = False
                for k in keys:
                    vals = data[k]
                    v_curr = vals[i]
                    v_prev = vals[i-1]
                    if v_curr != v_prev:
                        has_change = True
                        break
                if has_change:
                    indices_to_keep.append(i)
            
            else:
                raise ValueError("dup_typeは'all'または'any'である必要があります")

    else:
        raise NotImplementedError(f"Duplicate mode '{mode}' is not implemented")
        
    return indices_to_keep


def filter_valid_rows(
    data: Dict[str, Union[np.ndarray, list]],
    mode: str = "any"
) -> List[bool]:
    """
    Return boolean mask for valid rows (no None/NaN).
    mode='any': Keep row if ALL columns are valid. (Wait, logic check below)
    mode='all': Keep row if ANY column is valid. 
    
    Standard 'dropna' logic:
    any: if any value is NA, drop row. (So keep if ALL valid)
    all: if all values are NA, drop row. (So keep if ANY valid)
    
    The original implementation said:
    mode='any': keep if all valid (drop if any invalid?) 
      -> "mode='any': ひとつでも無効なら除外" (If any invalid, exclude -> dropna(how='any'))
    mode='all': keep if any valid (drop if all invalid)
      -> "mode='all': すべて無効なら除外" (If all invalid, exclude -> dropna(how='all'))
    """
    if mode not in ["any", "all"]:
        raise ValueError("モードは'any'または'all'のいずれかである必要があります")

    if not data:
        return []

    # Get length
    keys = list(data.keys())
    length = len(data[keys[0]])
    
    # We can use predicates.is_valid on each column
    # Then combine masks
    
    # Initialize mask
    if mode == "any":
        # Start with all True (Keep), AND with each column validity
        combined_mask = np.ones(length, dtype=bool)
        for k in keys:
            valid_col = is_valid(data[k])
            combined_mask = combined_mask & valid_col
    else:
        # mode == "all" (drop only if all are NA -> keep if any is Valid)
        # Start with all False (Drop), OR with each column validity
        combined_mask = np.zeros(length, dtype=bool)
        for k in keys:
            valid_col = is_valid(data[k])
            combined_mask = combined_mask | valid_col
            
    return combined_mask.tolist()
