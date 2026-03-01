"""
選択操作モジュール

このモジュールは選択操作（select）を提供します。
select は列名、行インデックス、ステップ値などを指定してデータを抽出する操作です。
"""

from typing import List, Optional, Dict, Any, Union, Tuple
import numpy as np
from ...core.collection import ColumnCollection
from ..registry import operation, register_functional
from ..abstraction import filter_rows, select_columns, inject_columns, inject_step_values
from ...functional import select as functional_select


select = register_functional(
    functional_select.select_indices,
    domain="core",
    name="select",
    select_columns={"arg_name": "columns"},
    filter_rows=True,
    inject_step_values={},
    signature_override={
        # columns is handled by select_columns, but passed to pure func (ignored there but arg exists)
    }
)
select.__doc__ = """条件（行や列）に基づいてデータを抽出し、新しいコレクションを作成します

    Args:
        collection (ColumnCollection): データコレクション
        columns (str | List[str], optional): 抽出するカラム名. Defaults to None (全カラム).
        start (int, optional): 抽出開始インデックス. Defaults to None.
        end (int, optional): 抽出終了インデックス. Defaults to None.
        step_min (float, optional): 最小ステップ値. Defaults to None.
        step_max (float, optional): 最大ステップ値. Defaults to None.
        
    Returns:
        ColumnCollection: 条件に一致するデータのみを含む新しいコレクション
"""


fetch_near_step = register_functional(
    functional_select.fetch_near_step,
    domain="core",
    name="fetch_near_step",
    inject_columns={"num_inputs": 1},
    filter_rows=True,
)
fetch_near_step.__doc__ = """指定ステップ値に最も近いデータ行を一つ抽出します

    Args:
        collection (ColumnCollection): データコレクション
        target_step (float): 抽出したい基準ステップ値
        
    Returns:
        ColumnCollection: ターゲットに最も近い1行のみを含む新しいコレクション（要素数1）
"""


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
    """
    length = len(collection)
    slices = functional_select.split_at_indices(length, indices)
    
    results = []
    for slc in slices:
        res = collection[slc]
        results.append(res)
        
    return results
