from typing import Any, Optional, Union, List, Dict
from ...core.collection import ColumnCollection
from ...core.column import Column
from ...core.step import Step
from ..registry import operation, register_functional
from ..abstraction import inject_columns, filter_rows, inject_step_values
from ...functional import predicates, row_ops
import inspect
import numpy as np


# Refactored to use functional core
filter_by_value = register_functional(
    predicates.eq,
    domain="core",
    name="filter_by_value",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    filter_rows=True,
    signature_override={
        "values": ("column", str),  # Map first arg 'values' to 'column' (str)
        # Preserve others
        "value": (Any, inspect.Parameter.empty),
        "tolerance": (Optional[float], None),
    }
)


filter_out_none = register_functional(
    row_ops.filter_valid_rows,
    domain="core",
    name="filter_out_none",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    filter_rows=True,
    signature_override={
        "data": ("columns", Optional[List[str]]),
        "mode": (str, "any")
    }
)


def _remove_consecutive_duplicates_adapter(
    data: Dict[str, Union[np.ndarray, List[Any]]], 
    columns: Optional[List[str]] = None, 
    dup_type: str = "all"
) -> List[int]:
    # dup_type 'all'/'any' in original implementation behave identically for consecutive check
    # (check if ANY column changed vs previous row -> keep)
    # This matches row_ops.duplicated_indices(mode="consecutive")
    if dup_type not in ["all", "any"]:
        raise ValueError("dup_typeは'all'または'any'である必要があります")
        
    return row_ops.duplicated_indices(data, mode="consecutive")


remove_consecutive_duplicates_across = register_functional(
    _remove_consecutive_duplicates_adapter,
    domain="core",
    name="remove_consecutive_duplicates_across",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    filter_rows=True,
    signature_override={
        "data": ("columns", Optional[List[str]]),
        "dup_type": (str, "all")
    }
)


@operation(domain="core")
@filter_rows
@inject_columns(num_inputs=1, cast_to_numpy=True)
def remove_outliers(
    vals: Any,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[bool]:
    """異常値を検出して除去した新しいコレクションを返します"""
    from ..core.stats import detect_outliers

    # vals is injected as numpy array (implied by cast_to_numpy=True)
    
    flags = detect_outliers(
        vals,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )

    if hasattr(flags, "__iter__") and not isinstance(flags, str):
         return [f == 0 for f in flags]
    else:
         return [flags == 0]


@operation(domain="core")
@filter_rows
@inject_columns(num_inputs=1, cast_to_numpy=True)
def filter_by_condition(
    vals: Any, condition: callable
) -> List[bool]:
    """指定された列の値が条件を満たす行をフィルタリングします"""
    # vals is numpy array
    return [condition(val) for val in vals]


@operation(domain="core")
@filter_rows
@inject_step_values
def remove_steps(
    step_values: Union[List[Any], np.ndarray],
    steps: List[Any], 
    tolerance: Optional[float] = None
) -> List[bool]:
    """指定されたステップ値を持つ行を削除します"""
    
    current_steps = step_values if isinstance(step_values, (list, np.ndarray)) else np.array(step_values)
    steps_to_remove = set(steps)

    if tolerance is None:
        mask = [s not in steps_to_remove for s in current_steps]
    else:
        mask = []
        steps_arr = np.array(steps)
        for s in current_steps:
            is_close = np.any(np.abs(steps_arr - s) <= tolerance)
            mask.append(not is_close)

    return mask


@operation(domain="core")
def filter_val(
    collection: ColumnCollection,
    column_name: str,
    value: Any,
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """filter_by_value のエイリアス"""
    return filter_by_value(
        collection, column_name, value, tolerance=tolerance
    )


@operation(domain="core")
def filter_cond(
    collection: ColumnCollection, column_name: str, condition: callable
) -> ColumnCollection:
    """filter_by_condition のエイリアス"""
    return filter_by_condition(collection, column_name, condition)


@operation(domain="core")
def rm_outliers(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> ColumnCollection:
    """remove_outliers のエイリアス"""
    return remove_outliers(
        collection,
        column,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )
