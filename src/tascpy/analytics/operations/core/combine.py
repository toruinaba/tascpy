"""Columnの合成操作

このモジュールでは、2つのColumnを合成するための操作関数を提供します。
特に、ステップやインデックスを基準にした条件付き合成やブレンド操作に焦点を当てています。
"""

from typing import Union, Optional, List, Dict, Any, Callable, Tuple
import numpy as np
import inspect
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column, NumberColumn, detect_column_type
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
switch_by_step.__doc__ = """特定のステップ値（またはインデックス）を境にして、2つのデータ列を切り替えます

    Args:
        collection (ColumnCollection): データコレクション
        v1 (str | np.ndarray): 切り替え前のデータ（カラム名または配列）
        v2 (str | np.ndarray): 切り替え後のデータ（カラム名または配列）
        threshold (int | float): 切り替えを実行する境界となるステップ値（またはインデックス）
        compare_mode (str, optional): 比較モード ("value", "index"). Defaults to "value".
        by_step_value (bool, optional): 基準軸としてステップ値を使うか. Defaults to True.
        tolerance (float, optional): 比較の許容誤差. Defaults to None.
        
    Returns:
        ColumnCollection: 切り替え済みのデータを持つ新しいコレクション
        
    Examples:
        >>> switched_col = col.ops.switch_by_step("Phase1", "Phase2", threshold=5.0)
"""



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
blend_by_step.__doc__ = """特定のステップ区間において、2つのデータ列を滑らかにブレンド（合成）します

    Args:
        collection (ColumnCollection): データコレクション
        v1 (str | np.ndarray): ブレンド前のデータ（始端側）
        v2 (str | np.ndarray): ブレンド後のデータ（終端側）
        start (int | float): ブレンドを開始するステップ値（またはインデックス）
        end (int | float): ブレンドを終了しv2に完全に以降するステップ値（またはインデックス）
        compare_mode (str, optional): 比較モード ("value", "index"). Defaults to "value".
        by_step_value (bool, optional): 基準軸としてステップ値を使うか. Defaults to True.
        blend_method (str, optional): ブレンド手法 ("linear", "cosine", "smoothstep"). Defaults to "linear".
        tolerance (float, optional): 比較の許容誤差. Defaults to None.

    Returns:
        ColumnCollection: ブレンド済みのデータを持つ新しいコレクション
        
    Examples:
        >>> blended_col = col.ops.blend_by_step("Phase1", "Phase2", start=4.0, end=6.0, blend_method="smoothstep")
"""


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
sum_columns.__doc__ = """指定された複数のカラムの要素ごとの合計を計算します

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 合計するカラム名のリスト. 未指定時はすべて. Defaults to None.
        
    Returns:
        ColumnCollection: 合計値カラムが追加された新しいコレクション
        
    Examples:
        >>> sum_col = col.ops.sum_columns(columns=["CH1", "CH2", "CH3"])
"""


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
average_columns.__doc__ = """指定された複数のカラムの要素ごとの平均を計算します

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 平均するカラム名のリスト. 未指定時はすべて. Defaults to None.
        
    Returns:
        ColumnCollection: 平均値カラムが追加された新しいコレクション
        
    Examples:
        >>> avg_col = col.ops.average_columns(columns=["CH1", "CH2", "CH3"])
"""


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
conditional_select.__doc__ = """条件列の値と閾値の比較結果に基づき、2つの列から値を選択します

    Args:
        collection (ColumnCollection): データコレクション
        v1 (str | np.ndarray): 条件付き真(True)の時に選ばれるデータ
        v2 (str | np.ndarray): 条件付き偽(False)の時に選ばれるデータ
        cond_values (str | np.ndarray): 条件判定の基準となるデータ列
        threshold (int | float, optional): 条件判定の閾値. Defaults to 0.
        compare (str, optional): 比較演算子 (">", "<", ">=", "<=", "==", "!="). Defaults to ">".
        
    Returns:
        ColumnCollection: 条件に基づいて選択されたデータを持つ新しいコレクション
        
    Examples:
        >>> selected_col = col.ops.conditional_select("CH_High", "CH_Low", cond_values="Temperature", threshold=50, compare=">")
"""


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
custom_combine.__doc__ = """ユーザー提供のカスタム関数を利用して2つの列を合成します

    Args:
        collection (ColumnCollection): データコレクション
        v1 (str | np.ndarray): 第一引数となるデータ列
        v2 (str | np.ndarray): 第二引数となるデータ列
        combine_func (Callable[[Any, Any], Any]): 合成処理を行うコールバック関数
        func_name (str, optional): 関数の名前（結果のカラム名に使用）. Defaults to None.
        
    Returns:
        ColumnCollection: カスタム加工されたデータを含む新しいコレクション
        
    Examples:
        >>> custom_col = col.ops.custom_combine("CH1", "CH2", combine_func=lambda x, y: x**2 + y**2, func_name="sum_squares")
"""
