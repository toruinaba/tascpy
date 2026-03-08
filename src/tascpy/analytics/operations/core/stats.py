"""
統計処理に関連する操作を提供するモジュール。
移動平均、異常値検出など、データの統計的処理のための関数を含みます。
"""

from typing import Optional, Any, Union, List
import numpy as np
from tascpy.core.collection import ColumnCollection
from ..registry import operation
from ..abstraction import store_result, inject_columns, handle_missing_values
from ...functional import stats as functional_stats
from ..naming import format_naming


@operation(domain="core")
@store_result(result_naming=format_naming(
    "ma{window_size}({0})",
    defaults={"window_size": 3},
    arg_names=["column", "window_size", "edge_handling"]
))
@inject_columns(num_inputs=1)
@handle_missing_values(strategy="nan")
def moving_average(
    collection: ColumnCollection,
    column: Union[str, np.ndarray],
    window_size: int = 3,
    edge_handling: str = "asymmetric",
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """指定されたウィンドウサイズで移動平均を計算します。

    Args:
        collection (ColumnCollection): データコレクション
        column (str): 計算対象のカラム名
        window_size (int, optional): 移動平均のウィンドウサイズ. Defaults to 3.
        edge_handling (str, optional): 端の処理方法 ("asymmetric", "symmetric"). Defaults to "asymmetric".
        result_column (str, optional): 結果を格納するカラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        ColumnCollection: 移動平均値が追加された新しいコレクション

    Examples:
        >>> smoothed_col = col.ops.moving_average("荷重", window_size=5)
    """
    return functional_stats.moving_average(column, window_size=window_size, edge_handling=edge_handling)


@operation(domain="core")
@store_result(result_naming=format_naming("outlier({0})"))
@inject_columns(num_inputs=1)
@handle_missing_values(strategy="nan")
def detect_outliers(
    collection: ColumnCollection,
    column: Union[str, np.ndarray],
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """異常値を検出し、フラグ（0: 正常, 1: 外れ値）を新しいカラムとして追加します。

    Args:
        collection (ColumnCollection): データコレクション
        column (str): 計算対象のカラム名
        window_size (int, optional): 移動平均のウィンドウサイズ. Defaults to 3.
        threshold (float, optional): 異常と判定する閾値. Defaults to 0.5.
        edge_handling (str, optional): 端の処理方法. Defaults to "asymmetric".
        min_abs_value (float, optional): ゼロ除算防止の最小絶対値. Defaults to 1e-10.
        scale_factor (float, optional): スケールファクタ. Defaults to 1.0.
        result_column (str, optional): 結果を格納するカラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        ColumnCollection: 異常値フラグが追加された新しいコレクション

    Examples:
        >>> flagged_col = col.ops.detect_outliers("変位", threshold=0.3)
    """
    return functional_stats.detect_outliers(
        column,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )


@operation(domain="core")
@store_result(result_naming=format_naming(
    "gaussian(col={0},sigma={sigma})",
    defaults={"sigma": 1.0},
    arg_names=["column", "sigma", "window_size"]
))
@inject_columns(num_inputs=1)
@handle_missing_values(strategy="nan")
def gaussian_filter(
    collection: ColumnCollection,
    column: Union[str, np.ndarray],
    sigma: float = 1.0,
    window_size: Optional[int] = None,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> ColumnCollection:
    """ガウシアンフィルターを適用して平滑化した値を新しいカラムとして追加します。

    Args:
        collection (ColumnCollection): データコレクション
        column (str): 計算対象のカラム名
        sigma (float, optional): ガウス分布の標準偏差. Defaults to 1.0.
        window_size (int, optional): フィルタウィンドウサイズ. 未指定時は sigma から自動計算. Defaults to None.
        result_column (str, optional): 結果を格納するカラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        ColumnCollection: フィルター処理後の値が追加された新しいコレクション

    Examples:
        >>> filtered_col = col.ops.gaussian_filter("荷重", sigma=2.0)
    """
    return functional_stats.gaussian_filter(column, sigma=sigma, window_size=window_size)
