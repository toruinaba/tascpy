"""Columnの合成操作

このモジュールでは、2つのColumnを合成するための操作関数を提供します。
特に、ステップやインデックスを基準にした条件付き合成やブレンド操作に焦点を当てています。
"""

from typing import Union, Optional, List, Dict, Any, Callable, Tuple
import numpy as np
from ...core.collection import ColumnCollection
from ...core.column import Column, NumberColumn, detect_column_type
from ..registry import operation, register_functional
from ..abstraction import inject_columns, store_result
from ...functional import combine as functional_combine




@operation(domain="core")
@store_result
@inject_columns(num_inputs=2, include_step=True, cast_to_numpy=True)
def switch_by_step(
    steps: np.ndarray,
    v1: np.ndarray,
    v2: np.ndarray,
    threshold: Union[int, float],
    compare_mode: str = "value",
    by_step_value: bool = True,
    result_column: Optional[str] = None,
    in_place: bool = False,
    tolerance: Optional[float] = None,
) -> Any:
    """ステップ値を基準に2つのColumnを切り替える (ベクトル化済み)"""
    new_values = functional_combine.switch_by_step(
        steps, v1, v2, threshold, 
        compare_mode=compare_mode, 
        by_step_value=by_step_value, 
        tolerance=tolerance
    )

    metadata = {
            "operation": "switch_by_step",
            "by_step_value": by_step_value,
            "compare_mode": compare_mode,
            "threshold": threshold,
    }
    return new_values, metadata


@operation(domain="core")
@store_result
@inject_columns(num_inputs=2, include_step=True, cast_to_numpy=True)
def blend_by_step(
    steps: np.ndarray,
    v1: np.ndarray,
    v2: np.ndarray,
    start: Union[int, float],
    end: Union[int, float],
    compare_mode: str = "value",
    by_step_value: bool = True,
    blend_method: str = "linear",
    result_column: Optional[str] = None,
    in_place: bool = False,
    tolerance: Optional[float] = None,
) -> Any:
    """ステップ値の範囲内で2つのColumnをブレンドする (ベクトル化済み)"""
    new_values = functional_combine.blend_by_step(
        steps, v1, v2, start, end,
        compare_mode=compare_mode,
        by_step_value=by_step_value,
        blend_method=blend_method,
        tolerance=tolerance
    )

    metadata = {
            "operation": "blend_by_step",
            "by_step_value": by_step_value,
            "compare_mode": compare_mode,
            "start": start,
            "end": end,
            "blend_method": blend_method,
    }
    return new_values, metadata


@operation(domain="core")
@store_result
@inject_columns(columns_arg="columns", cast_to_numpy=True)
def sum_columns(
    data: Dict[str, np.ndarray],
    columns: Optional[List[str]] = None,
) -> Any:
    """複数の列を合計します。
    
    指定した複数の列の値を要素ごとに合計し、結果の配列を返します。
    
    Args:
        data: 列データの辞書 (inject_columnsにより注入)
        columns: 合計対象の列名リスト
    """
    if not data:
        raise ValueError("合計対象の列が指定されていません")
    return functional_combine.sum_columns(list(data.values()))


@operation(domain="core")
@store_result
@inject_columns(columns_arg="columns", cast_to_numpy=True)
def average_columns(
    data: Dict[str, np.ndarray],
    columns: Optional[List[str]] = None,
) -> Any:
    """複数の列の平均値を計算します。
    
    指定した複数の列の値を要素ごとに平均し、結果の配列を返します。
    
    Args:
        data: 列データの辞書 (inject_columnsにより注入)
        columns: 平均対象の列名リスト
    """
    if not data:
        raise ValueError("平均対象の列が指定されていません")
    return functional_combine.average_columns(list(data.values()))


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


def _custom_combine_naming(operation_name, v1, v2, combine_func, func_name_arg=None, **kwargs):
    """custom_combine用の命名ロジック"""
    # func_name in arguments handles the `func_name` keyword argument of custom_combine
    # (inject_columns passes args/kwargs to inner func, and store_result calls inner func)
    # But store_result uses this naming strategy *before* calling inner func?
    # No, store_result calls inner func, gets data, THEN does naming.
    # So `args` and `kwargs` passed to naming strategy are ORIGINAL args/kwargs passed to wrapper.
    # Wrapper call: custom_combine(collection, "col1", "col2", combine_func=..., func_name="my_add")
    # args: ("col1", "col2"). kwargs: {combine_func:..., func_name:...}
    
    if func_name_arg:
        return func_name_arg
    # Check kwargs for func_name if passed as kwarg
    if "func_name" in kwargs and kwargs["func_name"]:
        return kwargs["func_name"]
        
    if hasattr(combine_func, "__name__") and combine_func.__name__ != "<lambda>":
        return combine_func.__name__
        
    # Check if combine_func is in kwargs
    if "combine_func" in kwargs:
         cf = kwargs["combine_func"]
         if hasattr(cf, "__name__") and cf.__name__ != "<lambda>":
             return cf.__name__

    return "custom_combine_result"


custom_combine = register_functional(
    functional_combine.custom_combine,
    domain="core",
    name="custom_combine",
    store_result={"result_naming": _custom_combine_naming},
    inject_columns={"num_inputs": 2, "cast_to_numpy": True},
    signature_override={
        "v1": ("v1", Any),
        "v2": ("v2", Any),
        "combine_func": ("combine_func", Callable[[Any, Any], Any]),
        "func_name": (Optional[str], None)
    }
)
