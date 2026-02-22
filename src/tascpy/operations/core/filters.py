from typing import Any, Optional, Union, List, Dict
from ...core.collection import ColumnCollection
from ...core.column import Column
from ...core.step import Step
from ..registry import operation, register_functional, register_pipeline
from ..abstraction import inject_columns, filter_rows, inject_step_values
from ...functional import filter_utils, stats as functional_stats
from ...functional import filters as functional_filters
import inspect
import numpy as np


# Refactored to use functional core
filter_by_value = register_functional(
    filter_utils.eq,
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
    filter_utils.filter_valid_rows,
    domain="core",
    name="filter_out_none",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    filter_rows=True,
    signature_override={
        "data": ("columns", Optional[List[str]]),
        "mode": (str, "any")
    }
)


remove_consecutive_duplicates_across = register_functional(
    filter_utils.duplicated_indices,
    domain="core",
    name="remove_consecutive_duplicates_across",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    filter_rows=True,
    signature_override={
        "data": ("columns", Optional[List[str]]),
        "mode": (str, "consecutive"),
        "dup_type": (str, "all")
    }
)



remove_outliers = register_pipeline(
    steps=[
        (functional_stats.detect_outliers, {}),
        (filter_utils.eq, {"value": 0}),
        (filter_rows, {})
    ],
    domain="core",
    name="remove_outliers",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "vals": ("column", str),
        "window_size": (int, 3),
        "threshold": (float, 0.5),
        "edge_handling": (str, "asymmetric"),
        "min_abs_value": (float, 1e-10),
        "scale_factor": (float, 1.0),
    }
)


filter_by_condition = register_functional(
    functional_filters.filter_by_condition,
    domain="core",
    name="filter_by_condition",
    filter_rows=True,
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "vals": ("column", str)
    }
)


remove_steps = register_functional(
    functional_filters.remove_steps_mask,
    domain="core",
    name="remove_steps",
    filter_rows=True,
    inject_step_values={},
    signature_override={
        # step_values injected, steps passed
    }
)


# ---------------------------------------------------------
# 検索操作 (search.pyから統合)
# ---------------------------------------------------------

search_by_value = register_functional(
    filter_utils.search,
    domain="core",
    name="search_by_value",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "values": ("values", Any),
    }
)


search_by_range = register_functional(
    filter_utils.search_range,
    domain="core",
    name="search_by_range",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "values": ("vals", Any),
    }
)


def _search_step_metadata(args, kwargs, result):
    min_val = kwargs.get("min", args[0] if len(args) > 0 else None)
    max_val = kwargs.get("max", args[1] if len(args) > 1 else None)
    inclusive = kwargs.get("inclusive", True)
    by_step_value = kwargs.get("by_step_value", True)
    
    return {
        "operation": "search_by_step_range",
        "by_step_value": by_step_value,
        "min": min_val,
        "max": max_val,
        "inclusive": inclusive,
    }


search_by_step_range = register_functional(
    filter_utils.search_step_range,
    domain="core",
    name="search_by_step_range",
    inject_step_values={"cast_to_numpy": True},
    inject_metadata=_search_step_metadata,
)


search_by_condition = register_functional(
    functional_filters.search_by_condition,
    domain="core",
    name="search_by_condition",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    signature_override={
        "data": ("columns", Optional[List[str]])
    }
)


search_missing_values = register_functional(
    functional_filters.search_missing_values,
    domain="core",
    name="search_missing_values",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    signature_override={
        "data": ("columns", Optional[List[str]])
    }
)


search_top_n = register_functional(
    filter_utils.top_n,
    domain="core",
    name="search_top_n",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "values": ("vals", Any),
    }
)


