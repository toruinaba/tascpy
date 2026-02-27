"""荷重-変位データの解析関数"""

from typing import List, Optional, Dict, Any, Tuple, Union
import numpy as np
from ...operations.registry import operation
from ...domains.load_displacement import LoadDisplacementCollection
from ...core.column import Column
from ...core.result import PointResult
from .utils import (
    get_load_column,
    get_displacement_column,
    get_load_data,
    get_displacement_data,
    get_valid_data,
)
from ...operations.validation import requires_domain
from ...operations.registry import register_functional
from .abstraction import resolve_ld_columns
from ...functional.load_displacement.analysis import compute_slopes, compute_stiffness, compute_yield_point

calculate_slopes = resolve_ld_columns(register_functional(
    compute_slopes,
    domain="load_displacement",
    name="calculate_slopes",
    inject_columns={"num_inputs": 2, "cast_to_numpy": True},
    store_result={"result_naming": "slope_data"},
    signature_override={
        "disp_data": ("column", float),
        "load_data": ("column", float),
    }
))

calculate_stiffness = resolve_ld_columns(register_functional(
    compute_stiffness,
    domain="load_displacement",
    name="calculate_stiffness",
    inject_columns={"num_inputs": 2, "cast_to_numpy": True},
    signature_override={
        "disp_data": ("column", float),
        "load_data": ("column", float),
        "range_start": (float, 0.2),
        "range_end": (float, 0.8),
        "method": (str, "linear_regression"),
    }
))

find_yield_point = resolve_ld_columns(register_functional(
    compute_yield_point,
    domain="load_displacement",
    name="find_yield_point",
    inject_columns={"num_inputs": 2, "cast_to_numpy": True},
    store_point_result={"name": "yield_point"},
    signature_override={
        "disp_data": ("column", float),
        "load_data": ("column", float),
        "method": (str, "offset"),
        "offset_value": (float, 0.002),
        "range_start": (float, 0.1),
        "range_end": (float, 0.3),
        "factor": (float, 0.33),
        "debug_mode": (bool, False),
        "fail_silently": (bool, False),
    }
))

stiffness = calculate_stiffness
yield_point = find_yield_point
