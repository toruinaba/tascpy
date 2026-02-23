"""
統計処理に関連する操作を提供するモジュール。
移動平均、異常値検出など、データの統計的処理のための関数を含みます。
"""

from typing import Optional, List, Dict, Any, Tuple, Union
import numpy as np
from ...core.collection import ColumnCollection
from ...core.column import Column, detect_column_type
from ..registry import operation, register_functional
from ..abstraction import transform_column, inject_columns, handle_missing_values
from ...functional import stats as functional_stats
from ..naming import format_naming

# --- Transformation Operations ---

moving_average = register_functional(
    functional_stats.moving_average,
    domain="core",
    name="moving_average",
    transform_column={
        "num_inputs": 1, 
        "result_naming": format_naming("ma{window_size}({0})", defaults={"window_size": 3}, arg_names=["vals", "window_size", "edge_handling"])
    },
    signature_override={
        "vals": ("vals", Any),
        "window_size": (int, 3),
        "edge_handling": (str, "asymmetric")
    }
)


detect_outliers = register_functional(
    functional_stats.detect_outliers,
    domain="core",
    name="detect_outliers",
    transform_column={"num_inputs": 1, "result_naming": format_naming("outlier({0})")},
    signature_override={
        "vals": ("vals", Any),
        "window_size": (int, 3),
        "threshold": (float, 0.5),
        "edge_handling": (str, "asymmetric"),
        "min_abs_value": (float, 1e-10),
        "scale_factor": (float, 1.0)
    }
)


gaussian_filter = register_functional(
    functional_stats.gaussian_filter,
    domain="core",
    name="gaussian_filter",
    transform_column={
        "num_inputs": 1, 
        "result_naming": format_naming("gaussian(col={0},sigma={sigma})", defaults={"sigma": 1.0}, arg_names=["vals", "sigma", "window_size"])
    },
    signature_override={
        "vals": ("vals", Any),
        "sigma": (float, 1.0),
        "window_size": (Optional[int], None)
    }
)






# --- Aggregation Operations ---

max = register_functional(
    functional_stats.calc_max,
    domain="core",
    name="max",
    inject_columns={"num_inputs": 1},
    extra_decorators=[handle_missing_values(strategy="nan")]
)

min = register_functional(
    functional_stats.calc_min,
    domain="core",
    name="min",
    inject_columns={"num_inputs": 1},
    extra_decorators=[handle_missing_values(strategy="nan")]
)

mean = register_functional(
    functional_stats.calc_mean,
    domain="core",
    name="mean",
    inject_columns={"num_inputs": 1},
    extra_decorators=[handle_missing_values(strategy="nan")]
)

std = register_functional(
    functional_stats.calc_std,
    domain="core",
    name="std",
    inject_columns={"num_inputs": 1},
    extra_decorators=[handle_missing_values(strategy="nan")]
)

sum = register_functional(
    functional_stats.calc_sum,
    domain="core",
    name="sum",
    inject_columns={"num_inputs": 1},
    extra_decorators=[handle_missing_values(strategy="nan")]
)
