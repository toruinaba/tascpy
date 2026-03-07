"""
統計処理に関連する操作を提供するモジュール。
移動平均、異常値検出など、データの統計的処理のための関数を含みます。
"""

from typing import Optional, List, Dict, Any, Tuple, Union
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column, detect_column_type
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
"""指定されたウィンドウサイズで移動平均を計算します

    Args:
        collection (ColumnCollection): データコレクション
        column_name (str): 計算対象のカラム名
        window_size (int, optional): 移動平均のウィンドウサイズ. Defaults to 3.
        edge_handling (str, optional): 端の処理方法 ("asymmetric", "symmetric", "constant", "mirror", "wrap"). Defaults to "asymmetric".
        
    Returns:
        ColumnCollection: 移動平均値が追加された新しいコレクション
        
    Examples:
        >>> smoothed_col = col.ops.moving_average("荷重", window_size=5)
"""
moving_average.__doc__ = """指定されたウィンドウサイズで移動平均を計算します

    Args:
        collection (ColumnCollection): データコレクション
        column_name (str): 計算対象のカラム名
        window_size (int, optional): 移動平均のウィンドウサイズ. Defaults to 3.
        edge_handling (str, optional): 端の処理方法 ("asymmetric", "symmetric", "constant", "mirror", "wrap"). Defaults to "asymmetric".
        
    Returns:
        ColumnCollection: 移動平均値が追加された新しいコレクション
        
    Examples:
        >>> smoothed_col = col.ops.moving_average("荷重", window_size=5)
"""


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
"""異常値を検出します

    Args:
        collection (ColumnCollection): データコレクション
        column_name (str): 計算対象のカラム名
        window_size (int, optional): 移動平均などのウィンドウサイズ. Defaults to 3.
        threshold (float, optional): 異常と判定する閾値. Defaults to 0.5.
        edge_handling (str, optional): 端の処理方法. Defaults to "asymmetric".
        min_abs_value (float, optional): ゼロ除算を防ぐための最小絶対値. Defaults to 1e-10.
        scale_factor (float, optional): スケールファクタ. Defaults to 1.0.

    Returns:
        ColumnCollection: 異常値フラグが追加された新しいコレクション
        
    Examples:
        >>> flagged_col = col.ops.detect_outliers("変位", threshold=3.0)
"""
detect_outliers.__doc__ = """異常値を検出します

    Args:
        collection (ColumnCollection): データコレクション
        column_name (str): 計算対象のカラム名
        window_size (int, optional): 移動平均などのウィンドウサイズ. Defaults to 3.
        threshold (float, optional): 異常と判定する閾値. Defaults to 0.5.
        edge_handling (str, optional): 端の処理方法. Defaults to "asymmetric".
        min_abs_value (float, optional): ゼロ除算を防ぐための最小絶対値. Defaults to 1e-10.
        scale_factor (float, optional): スケールファクタ. Defaults to 1.0.

    Returns:
        ColumnCollection: 異常値フラグが追加された新しいコレクション
        
    Examples:
        >>> flagged_col = col.ops.detect_outliers("変位", threshold=3.0)
"""


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
"""ガウシアンフィルターを適用します

    Args:
        collection (ColumnCollection): データコレクション
        column_name (str): 計算対象のカラム名
        sigma (float, optional): ガウス関数の標準偏差. Defaults to 1.0.
        window_size (Optional[int], optional): ウィンドウサイズ. Defaults to None.
        
    Returns:
        ColumnCollection: フィルター処理後の値が追加された新しいコレクション
        
    Examples:
        >>> filtered_col = col.ops.gaussian_filter("荷重", sigma=2.0)
"""
gaussian_filter.__doc__ = """ガウシアンフィルターを適用します

    Args:
        collection (ColumnCollection): データコレクション
        column_name (str): 計算対象のカラム名
        sigma (float, optional): ガウス関数の標準偏差. Defaults to 1.0.
        window_size (Optional[int], optional): ウィンドウサイズ. Defaults to None.
        
    Returns:
        ColumnCollection: フィルター処理後の値が追加された新しいコレクション
        
    Examples:
        >>> filtered_col = col.ops.gaussian_filter("荷重", sigma=2.0)
"""







