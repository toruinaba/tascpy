from typing import Any, Optional, Union, List, Callable
import numpy as np
from tascpy.core.collection import ColumnCollection
from ..registry import operation
from ..abstraction import inject_columns, filter_rows, inject_step_values
from ...functional import filters as functional_filters
from ...functional import stats as functional_stats


@operation(domain="core")
@filter_rows
@inject_columns(num_inputs=1, pass_collection=True)
def filter_by_value(
    collection: ColumnCollection,
    column: str,
    value: Any,
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """指定した列の値が条件に一致する行のみを抽出します。

    Args:
        collection (ColumnCollection): データコレクション
        column (str): 条件判定の対象となるカラム名
        value (Any): 一致するか比較する値
        tolerance (float, optional): 数値比較時の許容誤差. Defaults to None.

    Returns:
        ColumnCollection: 条件に一致した行のみを含む新しいコレクション

    Examples:
        >>> filtered_col = col.ops.filter_by_value("状態", "正常")
        >>> filtered_col = col.ops.filter_by_value("荷重", 100.0, tolerance=0.5)
    """
    # inject_columns により column は numpy 配列に変換済み
    return functional_filters.eq(column, value=value, tolerance=tolerance)


@operation(domain="core")
@filter_rows
def filter_out_none(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    mode: str = "any",
) -> ColumnCollection:
    """一つでも欠損値（None/NaN）が含まれる行、または全て欠損値の行を除外します。

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 判定対象のカラム名リスト. 未指定時はすべて. Defaults to None.
        mode (str, optional): 判定モード ("any": いずれかが欠損なら除外, "all": 全てが欠損なら除外). Defaults to "any".

    Returns:
        ColumnCollection: 欠損値を含む行が除外された新しいコレクション

    Examples:
        >>> clean_col = col.ops.filter_out_none()
        >>> clean_col = col.ops.filter_out_none(columns=["荷重", "変位"], mode="any")
    """
    target_cols = list(collection.columns.keys()) if columns is None else columns

    for col_name in target_cols:
        if col_name not in collection.columns:
            raise KeyError(f"列 '{col_name}' が存在しません")

    data = {name: np.array(collection[name].values) for name in target_cols}
    return functional_filters.filter_valid_rows(data, mode=mode)


@operation(domain="core")
@filter_rows
def remove_consecutive_duplicates_across(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    dup_type: str = "all",
) -> ColumnCollection:
    """連続する重複行を検知し、最初の行だけを残して除外します。

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 重複判定の対象となるカラム名リスト. 未指定時はすべて. Defaults to None.
        dup_type (str, optional): 重複判定方法 ("all": 全カラム一致で重複, "any": いずれかで重複). Defaults to "all".

    Returns:
        ColumnCollection: 連続重複が排除された新しいコレクション

    Examples:
        >>> thinned_col = col.ops.remove_consecutive_duplicates_across()
        >>> thinned_col = col.ops.remove_consecutive_duplicates_across(columns=["荷重", "変位"])
    """
    target_cols = list(collection.columns.keys()) if columns is None else columns

    for col_name in target_cols:
        if col_name not in collection.columns:
            raise KeyError(f"列 '{col_name}' が存在しません")

    data = {name: np.array(collection[name].values) for name in target_cols}
    return functional_filters.duplicated_indices(data, dup_type=dup_type)


@operation(domain="core")
@filter_rows
@inject_columns(num_inputs=1, pass_collection=True)
def filter_by_condition(
    collection: ColumnCollection,
    column: str,
    condition: Callable,
) -> ColumnCollection:
    """コールバック関数を使って、指定カラムの値に対するカスタム条件で行を抽出します。

    Args:
        collection (ColumnCollection): データコレクション
        column (str): 条件判定の対象となるカラム名
        condition (Callable): 各要素を受け取り True/False を返す関数

    Returns:
        ColumnCollection: 条件関数がTrueを返した行のみを含む新しいコレクション

    Examples:
        >>> high_load_col = col.ops.filter_by_condition("荷重", lambda x: x >= 50)
    """
    # inject_columns により column は numpy 配列に変換済み
    return functional_filters.filter_by_condition(column, condition=condition)


@operation(domain="core")
@filter_rows
def remove_outliers(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> ColumnCollection:
    """特定の基準（外れ値検知ロジック）に基づいて外れ値と判定された行を除外します。

    Args:
        collection (ColumnCollection): データコレクション
        column (str): 外れ値判定の対象となるカラム名
        window_size (int, optional): 移動窓のサイズ. Defaults to 3.
        threshold (float, optional): 外れ値と判定する閾値. Defaults to 0.5.
        edge_handling (str, optional): 端の処理手法 ("asymmetric", "symmetric"). Defaults to "asymmetric".
        min_abs_value (float, optional): 最小絶対値（ゼロ除算防止）. Defaults to 1e-10.
        scale_factor (float, optional): スケールファクター. Defaults to 1.0.

    Returns:
        ColumnCollection: 外れ値が除外された新しいコレクション

    Raises:
        KeyError: 指定されたカラムが存在しない場合

    Examples:
        >>> clean_col = col.ops.remove_outliers("変位", threshold=0.3)
    """
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' が存在しません")

    vals = np.array(collection[column].values)
    # detect_outliers returns list of 0/1 flags (1 = outlier)
    flags = functional_stats.detect_outliers(
        vals,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )
    # Keep only rows where flag == 0 (not outlier)
    return [i for i, f in enumerate(flags) if f == 0]


@operation(domain="core")
@filter_rows
@inject_step_values
def remove_steps(
    collection: ColumnCollection,
    steps: List[Any],
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """指定されたステップ値のリストに一致する行を除外します。

    Args:
        collection (ColumnCollection): データコレクション
        steps (List[float]): 除外したいステップ値のリスト
        tolerance (float, optional): ステップ値一致判定の許容誤差. Defaults to None.

    Returns:
        ColumnCollection: 指定したステップが除外された新しいコレクション

    Examples:
        >>> filtered_col = col.ops.remove_steps(steps=[1.0, 2.0, 3.0])
    """
    # inject_step_values により collection は step_values 配列になっている
    return functional_filters.remove_steps_mask(
        step_values=collection,
        steps=steps,
        tolerance=tolerance,
    )
