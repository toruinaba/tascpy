"""Columnの合成操作

このモジュールでは、2つのColumnを合成するための操作関数を提供します。
特に、ステップやインデックスを基準にした条件付き合成やブレンド操作に焦点を当てています。
"""

from typing import Union, Optional, List, Dict, Any, Callable, Tuple
import numpy as np
import inspect
from ...core.collection import ColumnCollection
from ...core.column import Column, NumberColumn, detect_column_type
from ..registry import operation, register_functional
from ..abstraction import inject_columns, store_result
from ...functional import combine as functional_combine



def _switch_by_step_metadata(args, kwargs, result):
    """Metadata generator for switch_by_step"""
    # args are inputs to the wrapper (excluding collection?)
    # wrapper(collection, v1, v2, threshold, ...)
    # args passed to inject_metadata are (v1, v2, threshold, ...)
    
    # Extract threshold (pos 2 or kwarg)
    threshold = kwargs.get("threshold")
    if threshold is None and len(args) > 2:
        threshold = args[2]
        
    compare_mode = kwargs.get("compare_mode", "value")
    by_step_value = kwargs.get("by_step_value", True)
    
    return {
        "operation": "switch_by_step",
        "by_step_value": by_step_value,
        "compare_mode": compare_mode,
        "threshold": threshold,
    }


switch_by_step = register_functional(
    functional_combine.switch_by_step,
    domain="core",
    name="switch_by_step",
    inject_columns={"num_inputs": 2, "include_step": True, "cast_to_numpy": True},
    store_result={},
    inject_metadata=_switch_by_step_metadata,
    signature_override={
        "steps": ("step_values", np.ndarray), # Injected
        "v1": ("v1", Union[str, np.ndarray]),
        "v2": ("v2", Union[str, np.ndarray]),
        "threshold": (Union[int, float], inspect.Parameter.empty),
        "compare_mode": (str, "value"),
        "by_step_value": (bool, True),
        "tolerance": (Optional[float], None)
    }
)



def _blend_by_step_metadata(args, kwargs, result):
    """Metadata generator for blend_by_step"""
    # args: (v1, v2, start, end, ...)
    start = kwargs.get("start")
    if start is None and len(args) > 2:
        start = args[2]

    end = kwargs.get("end")
    if end is None and len(args) > 3:
        end = args[3]
        
    compare_mode = kwargs.get("compare_mode", "value")
    by_step_value = kwargs.get("by_step_value", True)
    blend_method = kwargs.get("blend_method", "linear")
    
    return {
        "operation": "blend_by_step",
        "by_step_value": by_step_value,
        "compare_mode": compare_mode,
        "start": start,
        "end": end,
        "blend_method": blend_method,
    }

blend_by_step = register_functional(
    functional_combine.blend_by_step,
    domain="core",
    name="blend_by_step",
    inject_columns={"num_inputs": 2, "include_step": True, "cast_to_numpy": True},
    store_result={},
    inject_metadata=_blend_by_step_metadata,
    signature_override={
        "steps": ("step_values", np.ndarray),
        "v1": ("v1", np.ndarray),
        "v2": ("v2", np.ndarray),
        "start": (Union[int, float], inspect.Parameter.empty),
        "end": (Union[int, float], inspect.Parameter.empty),
        "compare_mode": (str, "value"),
        "by_step_value": (bool, True),
        "blend_method": (str, "linear"),
        "tolerance": (Optional[float], None),
    }
)


sum_columns = register_functional(
    lambda data, columns=None: functional_combine.sum_columns(list(data.values())),
    domain="core",
    name="sum_columns",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    store_result={},
    signature_override={
        "data": ("columns", Optional[List[str]]),
    }
)


average_columns = register_functional(
    lambda data, columns=None: functional_combine.average_columns(list(data.values())),
    domain="core",
    name="average_columns",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    store_result={},
    signature_override={
        "data": ("columns", Optional[List[str]]),
    }
)


conditional_select = register_functional(
    functional_combine.conditional_select,
    domain="core",
    name="conditional_select",
    store_result={},
    inject_columns={"num_inputs": 3, "cast_to_numpy": True},
    signature_override={
        "v1": ("v1", np.ndarray),
        "v2": ("v2", np.ndarray),
        "cond_values": ("cond_values", np.ndarray),
        "threshold": (Union[int, float], 0),
        "compare": (str, ">")
    }
)


from ..naming import callable_naming


custom_combine = register_functional(
    functional_combine.custom_combine,
    domain="core",
    name="custom_combine",
    store_result={"result_naming": callable_naming(callable_arg="combine_func", name_arg="func_name", default="custom_combine_result")},
    inject_columns={"num_inputs": 2, "cast_to_numpy": True},
    signature_override={
        "v1": ("v1", Any),
        "v2": ("v2", Any),
        "combine_func": ("combine_func", Callable[[Any, Any], Any]),
        "func_name": (Optional[str], None)
    }
)
