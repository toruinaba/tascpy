from typing import Any, List, Dict, Optional, Union, Callable
import operator
import numpy as np
from ...core.collection import ColumnCollection
from ..registry import operation, register_functional
from ..abstraction import filter_rows, inject_columns, inject_step_values
from ...functional import selectors, row_ops
import inspect


def _search_by_value_adapter(
    vals: Any, op_str: str, value: Any
) -> List[int]:
    return selectors.search(vals, op_str, value)


search_by_value = register_functional(
    _search_by_value_adapter,
    domain="core",
    name="search_by_value",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "vals": ("values", Any), # Just to be safe or maybe standard inference works
        # actually stub gen logic: first arg -> column. 
        # But wait, original stub had `vals: Any`. 
        # We want `column: str` in stub for the operation on Collection.
        # So "vals" -> "column".
    }
)


def _search_by_range_adapter(
    vals: Any,
    min_value: Any,
    max_value: Any,
    inclusive: bool = True,
) -> List[int]:
    return selectors.search_range(vals, min_value, max_value, inclusive)


search_by_range = register_functional(
    _search_by_range_adapter,
    domain="core",
    name="search_by_range",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        # vals mapped to column automatically by stub gen if first arg?
        # Yes.
    }
)


def _search_step_range_adapter(
    step_values: Union[List[Union[int, float]], np.ndarray],
    min: Union[int, float],  # Renamed from min_val to min to match Op
    max: Union[int, float],  # Renamed from max_val to max to match Op
    inclusive: bool = True,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> Union[List[int], tuple]:
    
    if by_step_value:
        indices = selectors.search_step_range(step_values, min, max, inclusive, tolerance)
    else:
        # Index based filtering
        length = len(step_values)
        indices = selectors.search_range(np.arange(length), min, max, inclusive)

    # メタデータを更新するためにタプルを返す
    metadata_update = {
        "operation": "search_by_step_range",
        "by_step_value": by_step_value,
        "min": min,
        "max": max,
        "inclusive": inclusive,
    }
    return indices, metadata_update


search_by_step_range = register_functional(
    _search_step_range_adapter,
    domain="core",
    name="search_by_step_range",
    inject_step_values={"cast_to_numpy": True},
    # No signature override needed for arg names if adapter matches
)


def _search_cond_pure(
    data: Dict[str, Any], 
    condition_func: Callable[[Dict[str, Any]], bool]
) -> List[int]:
    if not data:
        return []

    indices = []
    
    # Check length
    length = 0
    for arr in data.values():
        length = len(arr)
        break
    
    cols_data = data
    col_names = list(data.keys())
    
    for i in range(length):
        row_data = {}
        for name in col_names:
            vals = cols_data[name]
            if i < len(vals):
                 val = vals[i]
            else:
                 val = None
            row_data[name] = val

        if condition_func(row_data):
            indices.append(i)

    return indices


search_by_condition = register_functional(
    _search_cond_pure,
    domain="core",
    name="search_by_condition",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    signature_override={
        "data": ("columns", Optional[List[str]])
    }
)


def _search_missing_pure(data: Dict[str, Any]) -> List[int]:
    """Find indices of rows with missing values (any column)"""
    # This corresponds to keeping valid rows using "all" logic (keep if ANY valid -> NO)
    # We want rows that have ANY missing value.
    # filter_valid_rows(mode="any") returns True if ALL columns valid.
    # So missing rows are ~filter_valid_rows(mode="any").
    
    valid_mask = row_ops.filter_valid_rows(data, mode="any")
    # Invert mask
    missing_mask = [not x for x in valid_mask]
    return selectors.where(missing_mask)


search_missing_values = register_functional(
    _search_missing_pure,
    domain="core",
    name="search_missing_values",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    signature_override={
        "data": ("columns", Optional[List[str]])
    }
)


def _search_top_n_adapter(
    vals: Any, n: int, descending: bool = True
) -> List[int]:
    return selectors.top_n(vals, n, descending)


search_top_n = register_functional(
    _search_top_n_adapter,
    domain="core",
    name="search_top_n",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
)
