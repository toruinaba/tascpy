"""
選択操作モジュール

このモジュールは選択操作（select）を提供します。
select は列名、行インデックス、ステップ値などを指定してデータを抽出する操作です。
"""

from typing import List, Optional, Union
import numpy as np
from tascpy.core.collection import ColumnCollection
from ..registry import operation
from ..abstraction import filter_rows, select_columns, inject_step_values
from ...functional import select as functional_select


@operation(domain="core")
@select_columns(arg_name="columns")
@filter_rows
@inject_step_values
def select(
    collection: ColumnCollection,
    columns: Optional[List[str]] = None,
    indices: Optional[List[int]] = None,
    steps: Optional[List[Union[int, float]]] = None,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> ColumnCollection:
    """条件（行や列）に基づいてデータを抽出し、新しいコレクションを作成します。

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 抽出するカラム名のリスト. Defaults to None (全カラム).
        indices (List[int], optional): 抽出する行インデックスのリスト. Defaults to None.
        steps (List[float], optional): 抽出するステップ値またはインデックスのリスト. Defaults to None.
        by_step_value (bool, optional): `steps` をステップ値として扱うか（Falseはインデックス). Defaults to True.
        tolerance (float, optional): ステップ値一致判定の許容誤差. Defaults to None.

    Returns:
        ColumnCollection: 条件に一致するデータのみを含む新しいコレクション

    Raises:
        KeyError: 指定されたカラムが存在しない場合
        IndexError: 指定されたインデックスが範囲外の場合
        ValueError: `indices` と `steps` を同時に指定した場合

    Examples:
        >>> new_col = col.ops.select(columns=["荷重", "変位"])
        >>> sliced_col = col.ops.select(steps=[1.0, 2.0, 3.0])
        >>> sliced_col = col.ops.select(indices=[0, 2, 4])
    """
    # inject_step_values により collection は step_values 配列になっている
    return functional_select.select_indices(
        step_values=collection,
        indices=indices,
        steps=steps,
        by_step_value=by_step_value,
        tolerance=tolerance,
    )


@operation(domain="core")
@filter_rows
@inject_step_values
def fetch_near_step(
    collection: ColumnCollection,
    target_step: float,
) -> ColumnCollection:
    """指定ステップ値に最も近いデータ行を一つ抽出します。

    Args:
        collection (ColumnCollection): データコレクション
        target_step (float): 抽出したい基準ステップ値

    Returns:
        ColumnCollection: ターゲットに最も近い1行のみを含む新しいコレクション（要素数1）

    Examples:
        >>> single_row = col.ops.fetch_near_step(5.0)
        >>> print(single_row.step.values[0])
    """
    # inject_step_values により collection は step_values 配列になっている
    return functional_select.fetch_near_step(
        values=collection,
        value=target_step,
    )


# ---------------------------------------------------------
# 分割操作 (split.pyから統合)
# ---------------------------------------------------------

@operation(domain="core")
def split_by_integers(
    collection: ColumnCollection,
    markers: Union[List[int], np.ndarray]
) -> List[ColumnCollection]:
    """整数マーカーに基づいてコレクションを分割します。

    ユニークなマーカー値ごとに、そのマーカーに対応するデータを含む
    新しい ColumnCollection のリストを返します。

    Args:
        collection: 対象の ColumnCollection
        markers: 各要素に対応する整数マーカーのリストまたは配列。長さはコレクションの長さと一致する必要があります。

    Returns:
        List[ColumnCollection]: 分割されたコレクションのリスト

    Examples:
        >>> cycles = col.ops.split_by_integers(markers=[1, 1, 2, 2, 3])
    """
    length = len(collection)
    indices_list = functional_select.split_by_integers(length, markers)

    results = []
    for indices in indices_list:
        indices_array = np.array(indices)
        step_vals = np.array(collection.step.values)

        try:
            new_step = step_vals[indices_array].tolist()
        except IndexError:
            raise IndexError("指定されたインデックスが範囲外です")

        new_cols = {}
        for name, col in collection.columns.items():
            c_vals = np.array(col.values)
            new_vals = c_vals[indices_array].tolist()
            new_cols[name] = col.__class__(col.ch, col.name, col.unit, new_vals)

        res = collection.clone()
        res.step.values = new_step
        res.columns = new_cols
        results.append(res)

    return results


@operation(domain="core")
def split_at_indices(
    collection: ColumnCollection,
    indices: Union[int, List[int]]
) -> List[ColumnCollection]:
    """指定されたインデックスでコレクションを分割します。

    Args:
        collection: 対象の ColumnCollection
        indices: 分割点となるインデックス（またはそのリスト）

    Returns:
        List[ColumnCollection]: 分割されたコレクションのリスト

    Examples:
        >>> partial_cols = col.ops.split_at_indices([100, 200])
    """
    length = len(collection)
    slices = functional_select.split_at_indices(length, indices)

    results = []
    for slc in slices:
        res = collection[slc]
        results.append(res)

    return results
