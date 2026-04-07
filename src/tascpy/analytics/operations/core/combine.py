"""Columnの合成操作

このモジュールでは、2つのColumnを合成するための操作関数を提供します。
特に、ステップやインデックスを基準にした条件付き合成やブレンド操作に焦点を当てています。
"""

from typing import Union, Optional, List, Dict, Any, Callable
import numpy as np
from tascpy.core.collection import ColumnCollection
from ..registry import operation
from ..abstraction import inject_columns, store_result
from ...functional.core import combine as functional_combine
from ..naming import basic_naming, callable_naming


@operation(domain="core")
@store_result(result_naming=basic_naming("switch_by_step"))
@inject_columns(num_inputs=2, pass_collection=True)
def switch_by_step(
    collection: ColumnCollection,
    v1: Union[str, np.ndarray],
    v2: Union[str, np.ndarray],
    threshold: Union[int, float] = 0,
    compare_mode: str = "value",
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """特定のステップ値（またはインデックス）を境にして、2つのデータ列を切り替えます。

    Args:
        collection (ColumnCollection): データコレクション
        v1 (str | np.ndarray): 切り替え前のデータ（カラム名または配列）
        v2 (str | np.ndarray): 切り替え後のデータ（カラム名または配列）
        threshold (int | float): 切り替えを実行する境界となるステップ値（またはインデックス）
        compare_mode (str, optional): 比較モード ("value", "index"). Defaults to "value".
        by_step_value (bool, optional): 基準軸としてステップ値を使うか. Defaults to True.
        tolerance (float, optional): 比較の許容誤差. Defaults to None.
        result_column (str, optional): 結果カラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        ColumnCollection: 切り替え済みのデータを持つ新しいコレクション

    Examples:
        >>> switched_col = col.ops.switch_by_step("Phase1", "Phase2", threshold=5.0)
    """
    steps = np.array(collection.step.values)
    return functional_combine.switch_by_step(
        steps=steps,
        v1=v1,
        v2=v2,
        threshold=threshold,
        compare_mode=compare_mode,
        by_step_value=by_step_value,
        tolerance=tolerance,
    )


@operation(domain="core")
@store_result(result_naming=basic_naming("blend_by_step"))
@inject_columns(num_inputs=2, pass_collection=True)
def blend_by_step(
    collection: ColumnCollection,
    v1: Union[str, np.ndarray],
    v2: Union[str, np.ndarray],
    start: Union[int, float] = 0,
    end: Union[int, float] = 1,
    compare_mode: str = "value",
    by_step_value: bool = True,
    blend_method: str = "linear",
    tolerance: Optional[float] = None,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """特定のステップ区間において、2つのデータ列を滑らかにブレンド（合成）します。

    Args:
        collection (ColumnCollection): データコレクション
        v1 (str | np.ndarray): ブレンド前のデータ（始端側）
        v2 (str | np.ndarray): ブレンド後のデータ（終端側）
        start (int | float): ブレンドを開始するステップ値（またはインデックス）
        end (int | float): ブレンドを終了しv2に完全に移行するステップ値（またはインデックス）
        compare_mode (str, optional): 比較モード ("value", "index"). Defaults to "value".
        by_step_value (bool, optional): 基準軸としてステップ値を使うか. Defaults to True.
        blend_method (str, optional): ブレンド手法 ("linear", "smooth", "log", "exp"). Defaults to "linear".
        tolerance (float, optional): 比較の許容誤差. Defaults to None.
        result_column (str, optional): 結果カラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        ColumnCollection: ブレンド済みのデータを持つ新しいコレクション

    Examples:
        >>> blended_col = col.ops.blend_by_step("Phase1", "Phase2", start=4.0, end=6.0)
    """
    steps = np.array(collection.step.values)
    return functional_combine.blend_by_step(
        steps=steps,
        v1=v1,
        v2=v2,
        start=start,
        end=end,
        compare_mode=compare_mode,
        by_step_value=by_step_value,
        blend_method=blend_method,
        tolerance=tolerance,
    )


@operation(domain="core")
@store_result(result_naming=basic_naming("sum_columns"))
def sum_columns(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """指定された複数のカラムの要素ごとの合計を計算します。

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 合計するカラム名のリスト. 未指定時はすべて. Defaults to None.
        result_column (str, optional): 結果カラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        ColumnCollection: 合計値カラムが追加された新しいコレクション

    Examples:
        >>> sum_col = col.ops.sum_columns(columns=["CH1", "CH2", "CH3"])
    """
    target_cols = list(collection.columns.keys()) if columns is None else columns
    for col_name in target_cols:
        if col_name not in collection.columns:
            raise KeyError(f"列 '{col_name}' が存在しません")
    arrays = [np.array(collection[name].values) for name in target_cols]
    return functional_combine.sum_columns(arrays)


@operation(domain="core")
@store_result(result_naming=basic_naming("average_columns"))
def average_columns(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """指定された複数のカラムの要素ごとの平均を計算します。

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 平均するカラム名のリスト. 未指定時はすべて. Defaults to None.
        result_column (str, optional): 結果カラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        ColumnCollection: 平均値カラムが追加された新しいコレクション

    Examples:
        >>> avg_col = col.ops.average_columns(columns=["CH1", "CH2", "CH3"])
    """
    target_cols = list(collection.columns.keys()) if columns is None else columns
    for col_name in target_cols:
        if col_name not in collection.columns:
            raise KeyError(f"列 '{col_name}' が存在しません")
    arrays = [np.array(collection[name].values) for name in target_cols]
    return functional_combine.average_columns(arrays)


@operation(domain="core")
@store_result(result_naming=basic_naming("conditional_select"))
@inject_columns(num_inputs=3, pass_collection=True)
def conditional_select(
    collection: ColumnCollection,
    v1: Union[str, np.ndarray],
    v2: Union[str, np.ndarray],
    cond_values: Union[str, np.ndarray],
    threshold: Union[int, float] = 0,
    compare: str = ">",
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """条件列の値と閾値の比較結果に基づき、2つの列から値を選択します。

    Args:
        collection (ColumnCollection): データコレクション
        v1 (str | np.ndarray): 条件真(True)の時に選ばれるデータ
        v2 (str | np.ndarray): 条件偽(False)の時に選ばれるデータ
        cond_values (str | np.ndarray): 条件判定の基準となるデータ列
        threshold (int | float, optional): 条件判定の閾値. Defaults to 0.
        compare (str, optional): 比較演算子 (">", "<", ">=", "<=", "==", "!="). Defaults to ">".
        result_column (str, optional): 結果カラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        ColumnCollection: 条件に基づいて選択されたデータを持つ新しいコレクション

    Examples:
        >>> selected_col = col.ops.conditional_select("CH_High", "CH_Low", "Temperature", threshold=50)
    """
    return functional_combine.conditional_select(
        v1=v1,
        v2=v2,
        cond_values=cond_values,
        threshold=threshold,
        compare=compare,
    )


@operation(domain="core")
@store_result(result_naming=callable_naming(callable_arg="combine_func", name_arg="func_name", default="custom_combine_result"))
@inject_columns(num_inputs=2, pass_collection=True)
def custom_combine(
    collection: ColumnCollection,
    v1: Union[str, np.ndarray],
    v2: Union[str, np.ndarray],
    combine_func: Callable[[Any, Any], Any] = None,
    func_name: Optional[str] = None,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """ユーザー提供のカスタム関数を利用して2つの列を合成します。

    Args:
        collection (ColumnCollection): データコレクション
        v1 (str | np.ndarray): 第一引数となるデータ列
        v2 (str | np.ndarray): 第二引数となるデータ列
        combine_func (Callable[[Any, Any], Any]): 合成処理を行うコールバック関数
        func_name (str, optional): 関数の名前（結果のカラム名に使用）. Defaults to None.
        result_column (str, optional): 結果カラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        ColumnCollection: カスタム加工されたデータを含む新しいコレクション

    Examples:
        >>> custom_col = col.ops.custom_combine("CH1", "CH2",
        ...     combine_func=lambda x, y: x**2 + y**2, func_name="sum_squares")
    """
    return functional_combine.custom_combine(v1=v1, v2=v2, combine_func=combine_func)
