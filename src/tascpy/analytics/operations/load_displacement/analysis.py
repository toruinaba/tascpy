"""荷重-変位データの解析関数"""

from typing import List, Optional, Dict, Any, Tuple, Union
import numpy as np
from ...operations.registry import operation
from tascpy.domains.load_displacement import LoadDisplacementCollection
from ...operations.abstraction import inject_columns, store_result, store_point_result, store_scalar_result
from ...functional.load_displacement.analysis import compute_slopes, compute_stiffness, compute_yield_point


@operation(domain="load_displacement")
@store_result(result_naming="slope_data")
def calculate_slopes(
    collection: LoadDisplacementCollection,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> LoadDisplacementCollection:
    """荷重-変位データから区間ごとの傾き（スロープ）を計算します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        result_column (str, optional): 結果カラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        LoadDisplacementCollection: 算出された傾きデータが追加された新しいコレクション

    Examples:
        >>> col = col.ops.calculate_slopes()
    """
    # Extract data directly from the collection
    disp_data = collection.displacement_data
    load_data = collection.load_data
    return compute_slopes(disp_data, load_data)


@operation(domain="load_displacement")
@store_scalar_result(name="stiffness")
def calculate_stiffness(
    collection: LoadDisplacementCollection,
    range_start: float = 0.2,
    range_end: float = 0.8,
    method: str = "linear_regression",
) -> LoadDisplacementCollection:
    """指定された範囲のデータから剛性（代表スロープ）を計算します。

    注意:
        変位データに変動がない（同じ値が連続する）場合、計算（SVD）がエラーになるか
        ゼロ除算が発生します。事前に `.ops.remove_consecutive_duplicates_across()` によって
        重複を除去しておくことを推奨します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        range_start (float, optional): 計算対象範囲の開始比率（最大値に対する比率）. Defaults to 0.2.
        range_end (float, optional): 計算対象範囲の終了比率（最大値に対する比率）. Defaults to 0.8.
        method (str, optional): 計算手法 ("linear_regression", "secant"). Defaults to "linear_regression".

    Returns:
        float: 計算された剛性値

    Examples:
        >>> stiffness = col.ops.calculate_stiffness(range_start=0.1, range_end=0.4)
    """
    disp_arr = collection.displacement_data
    load_arr = collection.load_data

    return compute_stiffness(
        disp_arr, load_arr,
        range_start=range_start,
        range_end=range_end,
        method=method,
    )


@operation(domain="load_displacement")
@store_point_result(name="yield_point")
def find_yield_point(
    collection: LoadDisplacementCollection,
    method: str = "offset",
    offset_value: float = 0.002,
    range_start: float = 0.1,
    range_end: float = 0.3,
    factor: float = 0.33,
    debug_mode: bool = False,
    fail_silently: bool = False,
) -> Tuple[bool, float, float, Dict[str, Any]]:
    """荷重-変位データから降伏点（Yield Point）を検出します。

    初期剛性を `range_start` から `range_end` の最大荷重に対する割合の範囲で自動計算し、
    以下のいずれかの手法で降伏点を求めます：

    - `method="offset"`: 初期剛性に対して `offset_value` 平行移動した直線とデータの交点。
    - `method="general"`: 各点の瞬間の傾き（勾配）を計算し、`initial_slope * factor` を下回った点。

    注意:
        変位データに変動がない（同じ変位値が連続する）場合、SVDエラーやゼロ除算が発生します。
        事前に `.ops.remove_consecutive_duplicates_across()` を実行してください。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        method (str, optional): 降伏点判定手法 ("offset", "max_load"). Defaults to "offset".
        offset_value (float, optional): オフセット法におけるオフセット値. Defaults to 0.002.
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
    disp_data = collection.displacement_data
    load_data = collection.load_data

    return compute_yield_point(
        disp_data, load_data,
        method=method,
        offset_value=offset_value,
        range_start=range_start,
        range_end=range_end,
        factor=factor,
        debug_mode=debug_mode,
        fail_silently=fail_silently,
    )


# Aliases
stiffness = calculate_stiffness
stiffness.__doc__ = "calculate_stiffness のエイリアス"

yield_point = find_yield_point
yield_point.__doc__ = "find_yield_point のエイリアス"
