
from typing import Dict, Any, List, Callable, Optional
import numpy as np
from . import selectors, row_ops

def search_by_condition(
    data: Dict[str, Any], 
    condition_func: Callable[[Dict[str, Any]], bool]
) -> List[int]:
    """
    Find indices where condition_func(row_dict) is True.
    """
    if not data:
        return []

    indices = []
    
    # Check length
    length = 0
    # Prefer first column's length
    for arr in data.values():
        length = len(arr)
        break
    
    col_names = list(data.keys())
    
    for i in range(length):
        row_data = {}
        for name in col_names:
            vals = data[name]
            if i < len(vals):
                 val = vals[i]
            else:
                 val = None
            row_data[name] = val

        if condition_func(row_data):
            indices.append(i)

    return indices

def search_missing_values(data: Dict[str, Any]) -> List[int]:
    """
    Find indices of rows with any missing values.
    """
    # Keep rows where ALL columns are valid (valid_mask is True)
    # So rows with missing values are where valid_mask is False
    valid_mask = row_ops.filter_valid_rows(data, mode="any")
    
    # Invert mask to find rows WITH missing values
    missing_mask = [not x for x in valid_mask]
    return selectors.where(missing_mask)
