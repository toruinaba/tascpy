"""
統計処理に関連する操作を提供するモジュール。
移動平均、異常値検出など、データの統計的処理のための関数を含みます。
"""

from typing import Optional, List, Dict, Any, Tuple, Union
import numpy as np
from ...utils.data import moving_average as utils_moving_average
from ...core.collection import ColumnCollection
from ...core.column import Column, detect_column_type
from ..registry import operation, register_functional
from ..abstraction import transform_column, inject_columns, handle_missing_values
from ...functional import stats as functional_stats

# --- Transformation Operations ---

def _ma_naming(func_name, col_name, **kwargs):
    window_size = kwargs.get("window_size", 3)
    return f"ma{window_size}({col_name})"

moving_average = register_functional(
    functional_stats.moving_average,
    domain="core",
    name="moving_average",
    transform_column={"num_inputs": 1, "result_naming": _ma_naming},
    signature_override={
        "vals": ("vals", Any),
        "window_size": (int, 3),
        "edge_handling": (str, "asymmetric")
    }
)


def _outlier_naming(func_name, col_name, **kwargs):
    return f"outlier({col_name})"

detect_outliers = register_functional(
    functional_stats.detect_outliers,
    domain="core",
    name="detect_outliers",
    transform_column={"num_inputs": 1, "result_naming": _outlier_naming},
    signature_override={
        "vals": ("vals", Any),
        "window_size": (int, 3),
        "threshold": (float, 0.5),
        "edge_handling": (str, "asymmetric"),
        "min_abs_value": (float, 1e-10),
        "scale_factor": (float, 1.0)
    }
)


def _gaussian_naming(func_name, col_name, **kwargs):
    sigma = kwargs.get("sigma", 1.0)
    return f"gaussian(col={col_name},sigma={sigma})"

gaussian_filter = register_functional(
    functional_stats.gaussian_filter,
    domain="core",
    name="gaussian_filter",
    transform_column={"num_inputs": 1, "result_naming": _gaussian_naming},
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
