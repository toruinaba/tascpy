"""
選択操作モジュール

このモジュールは選択操作（select）を提供します。
select は列名、行インデックス、ステップ値などを指定してデータを抽出する操作です。
"""

from typing import List, Optional, Dict, Any, Union, Tuple
import numpy as np
from ...core.collection import ColumnCollection
from ..registry import operation, register_functional
from ..abstraction import filter_rows, select_columns, inject_columns, inject_step_values, split_result, inject_length
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


fetch_near_step = register_functional(
    functional_select.fetch_near_step,
    domain="core",
    name="fetch_near_step",
    inject_columns={"num_inputs": 1},
    filter_rows=True,
)


# ---------------------------------------------------------
# 分割操作 (split.pyから統合)
# ---------------------------------------------------------

split_by_integers = register_functional(
    functional_select.split_by_integers,
    domain="core",
    name="split_by_integers",
    extra_decorators=[inject_length, split_result],
    signature_override={
        "length": ("length", int),
        "markers": ("markers", List[int])
    }
)


split_at_indices = register_functional(
    functional_select.split_at_indices,
    domain="core",
    name="split_at_indices",
    extra_decorators=[inject_length, split_result],
    signature_override={
        "length": ("length", int),
        "indices": ("indices", Union[int, List[int]])
    }
)
