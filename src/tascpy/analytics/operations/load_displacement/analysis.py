"""荷重-変位データの解析関数"""

from typing import List, Optional, Dict, Any, Tuple, Union
import numpy as np
from ...operations.registry import operation
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.core.column import Column
from tascpy.core.result import PointResult
from ...operations.validation import requires_domain
from ...operations.registry import register_functional
from .abstraction import resolve_ld_columns
from ...functional.load_displacement.analysis import compute_slopes, compute_stiffness, compute_yield_point

calculate_slopes = operation(domain="load_displacement")(resolve_ld_columns(register_functional(
    compute_slopes,
    domain="load_displacement",
    name="calculate_slopes",
    inject_columns={"num_inputs": 2, "cast_to_numpy": True},
    store_result={"result_naming": "slope_data"},
    signature_override={
        "disp_data": ("column", float),
    }
)))
calculate_slopes.__doc__ = """荷重-変位データから区間ごとの傾き（スロープ）を計算します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        disp_data (str, optional): 変位データのカラム名（None時は自動解決）
        load_data (str, optional): 荷重データのカラム名（None時は自動解決）
        
    Returns:
        LoadDisplacementCollection: 算出された傾きデータが追加された新しいコレクション
        
    Examples:
        >>> col = col.ops.calculate_slopes()
"""

calculate_stiffness = operation(domain="load_displacement")(resolve_ld_columns(register_functional(
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
)))
calculate_stiffness.__doc__ = """指定された範囲のデータから剛性（代表スロープ）を計算します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        disp_data (str, optional): 変位データのカラム名（None時は自動解決）
        load_data (str, optional): 荷重データのカラム名（None時は自動解決）
        range_start (float, optional): 計算対象範囲の開始比率（最大値に対する比率）. Defaults to 0.2.
        range_end (float, optional): 計算対象範囲の終了比率（最大値に対する比率）. Defaults to 0.8.
        method (str, optional): 計算手法 ("linear_regression", "secant"). Defaults to "linear_regression".
        
    Returns:
        LoadDisplacementCollection: 剛性の計算結果がメタデータとして追加された新しいコレクション
        
    Examples:
        >>> col = col.ops.calculate_stiffness(range_start=0.1, range_end=0.4, method="linear_regression")
"""

find_yield_point = operation(domain="load_displacement")(resolve_ld_columns(register_functional(
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
)))
find_yield_point.__doc__ = """荷重-変位データから降伏点（Yield Point）を検出します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        disp_data (str, optional): 変位データのカラム名（None時は自動解決）
        load_data (str, optional): 荷重データのカラム名（None時は自動解決）
        method (str, optional): 降伏点判定手法 ("offset", "max_load"). Defaults to "offset".
        offset_value (float, optional): オフセット法におけるオフセットひずみ等. Defaults to 0.002.
        range_start (float, optional): 剛性計算の開始比率. Defaults to 0.1.
        range_end (float, optional): 剛性計算の終了比率. Defaults to 0.3.
        factor (float, optional): 特定手法での係数. Defaults to 0.33.
        debug_mode (bool, optional): デバッグ情報を表示するか. Defaults to False.
        fail_silently (bool, optional): 検出失敗時に例外を投げず無視するか. Defaults to False.
        
    Returns:
        LoadDisplacementCollection: 降伏点情報が結果として追加された新しいコレクション
        
    Examples:
        >>> col = col.ops.find_yield_point(method="offset", offset_value=0.002)
        >>> yield_pt = col.results["yield_point"].value
"""

stiffness = calculate_stiffness
stiffness.__doc__ = "calculate_stiffness のエイリアス"

yield_point = find_yield_point
yield_point.__doc__ = "find_yield_point のエイリアス"
