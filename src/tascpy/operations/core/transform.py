import math
import numpy as np
from typing import Union, Optional, List, Dict, Any, Callable
from ...core.collection import ColumnCollection
from ...core.column import Column, detect_column_type
from ..registry import operation, register_functional
from ..abstraction import transform_column
from ...functional import transform as functional_transform
from ..naming import basic_naming, format_naming


# ---------------------------------------------------------
# Naming Helpers
# ---------------------------------------------------------

def _get_col_name(args, kwargs):
    """Helper to extract column name from args or kwargs"""
    if len(args) > 0:
        return args[0]
    return kwargs.get("column")

def _log_naming(func_name, *args, base=math.e, **kwargs):
    col = _get_col_name(args, kwargs)
    # Check if base is passed as positional arg (arg index 1)
    if len(args) > 1:
        base = args[1]
    
    if base == math.e:
        return f"log({col})"
    elif base == 10:
        return f"log10({col})"
    else:
        return f"log{base}({col})"


# ---------------------------------------------------------
# Operations
# ---------------------------------------------------------

# 三角関数
sin = register_functional(
    functional_transform.sin,
    domain="core",
    name="sin",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray), "degrees": (bool, False)}
)


cos = register_functional(
    functional_transform.cos,
    domain="core",
    name="cos",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray), "degrees": (bool, False)}
)


tan = register_functional(
    functional_transform.tan,
    domain="core",
    name="tan",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray), "degrees": (bool, False)}
)


# 指数関数/対数関数
exp = register_functional(
    functional_transform.exp,
    domain="core",
    name="exp",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray)}
)


log = register_functional(
    functional_transform.log,
    domain="core",
    name="log",
    transform_column={"num_inputs": 1, "result_naming": _log_naming},
    signature_override={"values": ("values", np.ndarray), "base": (float, math.e)}
)


sqrt = register_functional(
    functional_transform.sqrt,
    domain="core",
    name="sqrt",
    transform_column={"num_inputs": 1, "result_naming": basic_naming},
    signature_override={"values": ("values", np.ndarray)}
)


pow = register_functional(
    functional_transform.power,
    domain="core",
    name="pow",
    transform_column={
        "num_inputs": 1, 
        "result_naming": format_naming("{0}^{exponent}", defaults={"exponent": 1.0}, arg_names=["values", "exponent"])
    },
    signature_override={"values": ("values", np.ndarray), "exponent": (float, 1.0)}
)


# その他の変換関数
abs_values = register_functional(
    functional_transform.abs_values,
    domain="core",
    name="abs_values",
    transform_column={"num_inputs": 1, "result_naming": format_naming("abs({0})")},
    signature_override={"values": ("values", np.ndarray)}
)

abs = abs_values
# Note: abs is explicitly registered as standard op via register_functional, 
# and aliasing shares it, but `abs` builtin name conflict is intentional.
# Original implementation: abs = abs_values.
# If we re-register `abs`, it might be safer, but alias works if `register_functional` returns the wrapped function.
# Yes it does.
# However, `abs` variable name overrides builtin `abs`. This is intentional in original.

# Also register 'abs' explicitly to be safe? 
# No, `abs_values` is registered. `abs = abs_values` just aliases the variable.
# But `@operation` on `abs_values` registered it as `abs_values`. 
# If want `abs` operation, we might need to register it.
# Original: just `abs = abs_values`.
# If `abs_values` was decorated, `abs` refers to the wrapper.
# So users can invoke `core.transform.abs(col)`.
# And registry has "abs_values". 
# Registry does NOT have "abs" unless `abs` variable was decorated independently?
# No, original code:
# @operation ... def abs_values ...
# abs = abs_values
# So registry has "abs_values". `abs` is just Python alias.
# Users calling `transform.abs(...)` works as function call.
# `collection.apply(transform.abs)` works.
# `collection.apply("abs")` would FAIL in original code?
# Yes.
# So this refactor maintains that behavior.


round_values = register_functional(
    functional_transform.round_values,
    domain="core",
    name="round_values",
    transform_column={"num_inputs": 1, "result_naming": format_naming("round({0}, {decimals})", defaults={"decimals": 0})},
    signature_override={"values": ("values", np.ndarray), "decimals": (int, 0)}
)


normalize = register_functional(
    functional_transform.normalize,
    domain="core",
    name="normalize",
    transform_column={"num_inputs": 1, "result_naming": format_naming("norm_{method}({0})", defaults={"method": "minmax"})},
    signature_override={"values": ("values", np.ndarray), "method": (str, "minmax")}
)
