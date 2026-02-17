from typing import Any, List, Dict, Optional, Union, Callable
import operator
import numpy as np
from ...core.collection import ColumnCollection
from ..registry import operation, register_functional
from ..abstraction import filter_rows, inject_columns, inject_step_values
from ...functional import selectors, row_ops
from ...functional import search as functional_search
import inspect


search_by_value = register_functional(
    selectors.search,
    domain="core",
    name="search_by_value",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "values": ("vals", Any),  # Renaming 'values' arg of pure func to 'vals' in op to match original adapter's first arg?
        # Original adapter sig: (vals: Any, op_str: str, value: Any)
        # So operation signature exposed 'vals'. 
        # Wait, inject_columns replaces the first argument with data.
        # But 'vals' would be the name of the column ARGUMENT in the wrapper? 
        # No, inject_columns(num_inputs=1) implies the first POSITIONAL argument of the created wrapper is the column name.
        # The name of that argument in the wrapper is determined by signature_override or inferred.
        # If I want the wrapper to have `def search_by_value(vals: Any, ...)` I should map "values" -> "vals".
        # Actually standard practice is "column". But original code had "vals" in adapter.
        # Let's verify `test_search.py` usage.
        # `test_search.py`: `search_by_value(col, "A", ...)` or `ops.search_by_value("A", ...)`
        # If I change arg name to "column", it's safer.
        # Let's map "values" -> "vals" to be conservative with original adapter name, OR "column" if cleaner.
        # Original core operation usually takes "column".
        # Let's look at `search_by_value` usages.
        # Actually `inject_columns` with `num_inputs=1` creates `column` arg by default if not tailored?
        # No, it injects into the functional arg.
        # The wrapper arg name comes from signature override.
        # Previous override: `"vals": ("values", Any)`. Wait.
        # Adapter had `vals`. Override mapped `vals` (adapter arg) to `values` (wrapper arg)?
        # No, `signature_override` maps { "internal_arg": ("exposed_name", type) }.
        # Previous: `"vals": ("values", Any)`. So wrapper had `values`.
        # Adapter: `def _search_by_value_adapter(vals, ...)`
        # So `vals` was internal. `values` was exposed.
        # So I should map `selectors.search`'s `values` -> `values`.
        # `values`: ("values", Any).
        "values": ("values", Any),
    }
)


search_by_range = register_functional(
    selectors.search_range,
    domain="core",
    name="search_by_range",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "values": ("values", Any),
        "min_val": ("min_value", Any),
        "max_val": ("max_value", Any),
    }
)


def _search_step_metadata(args, kwargs, result):
    # args: (steps, min_val, max_val, ...)
    # But inject_step_values injects 'steps' into the first argument.
    # The wrapper args are (min, max, inclusive=True, by_step_value=True, tolerance=None).
    # Step values are injected.
    # result is (indices, metadata).
    # But wait, search_step_range pure func returns List[int].
    # We need to return (indices, metadata) to match original adapter?
    # Original adapter returned `(indices, metadata_update)`.
    # `register_functional` with `store_result`?
    # No, `search` operations usually return `Indices` object (which is just list + metadata update? No.)
    # `search` ops return `List[int]` or `Indices`.
    # If pure func returns list, `register_functional` wraps it.
    # If we want to return metadata update from pure func, we use `(result, metadata)` tuple.
    # `selectors.search_step_range` returns `List[int]`.
    # We need to inject metadata.
    # `register_functional` has `inject_metadata`.
    
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
    selectors.search_step_range,
    domain="core",
    name="search_by_step_range",
    inject_step_values={"cast_to_numpy": True},
    inject_metadata=_search_step_metadata,
    signature_override={
        "steps": ("step_values", np.ndarray), # Injected
        "min_val": ("min", Union[int, float]),
        "max_val": ("max", Union[int, float]),
    }
)


search_top_n = register_functional(
    selectors.top_n,
    domain="core",
    name="search_top_n",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "values": ("vals", Any), # Original adapter named it 'vals'
        # Check `_search_top_n_adapter(vals, ...)`
        # `operations/core/search.py` previous had NO signature override for `search_top_n`?
        # Yes, lines 120-125.
        # So wrapper args were inferred from adapter: `vals`, `n`, `descending`.
        # `selectors.top_n` has `values`.
        # So we map `values` -> `vals`.
    }
)
