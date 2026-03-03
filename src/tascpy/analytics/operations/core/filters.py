from typing import Any, Optional, Union, List, Dict
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.core.step import Step
from ..registry import operation, register_functional, register_pipeline
from ..abstraction import inject_columns, filter_rows, inject_step_values
from ...functional import filters, stats as functional_stats
from ...functional import filters as filters
import inspect
import numpy as np


# Refactored to use functional core
filter_by_value = register_functional(
    filters.eq,
    domain="core",
    name="filter_by_value",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    filter_rows=True,
    signature_override={
        "values": ("column", str),  # Map first arg 'values' to 'column' (str)
        # Preserve others
        "tolerance": (Optional[float], None),
    }
)
filter_by_value.__doc__ = """指定した列の値が条件に一致する行のみを抽出します。

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


filter_out_none = register_functional(
    filters.filter_valid_rows,
    domain="core",
    name="filter_out_none",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    filter_rows=True,
    signature_override={
        "mode": (str, "any")
    }
)
filter_out_none.__doc__ = """一つでも欠損値（None/NaN）が含まれる行、または全て欠損値の行を除外します。

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 判定対象のカラム名リスト. 未指定時はすべて. Defaults to None.
        mode (str, optional): 判定モード ("any": いずれかが欠損なら除外, "all": 全てが欠損なら除外). Defaults to "any".
        
    Returns:
        ColumnCollection: 欠損値を含む行が除外された新しいコレクション
        
    Examples:
        >>> clean_col = col.ops.filter_out_none() # どこかに欠損があればその行を削除
"""


remove_consecutive_duplicates_across = register_functional(
    filters.duplicated_indices,
    domain="core",
    name="remove_consecutive_duplicates_across",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    filter_rows=True,
    signature_override={
        "data": ("columns", Optional[List[str]]),
        "dup_type": (str, "all")
    }
)
remove_consecutive_duplicates_across.__doc__ = """連続する重複行を検知し、最初の行だけを残して除外します。

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 重複判定の対象となるカラム名リスト. 未指定時はすべて. Defaults to None.
        mode (str, optional): 重複判定モード. Defaults to "consecutive".
        dup_type (str, optional): どの重複を残すか. Defaults to "all".
        
    Returns:
        ColumnCollection: 連続重複が排除された新しいコレクション
        
    Examples:
        >>> # 値が変化しない静止状態のデータを間引く場合などに有用
        >>> thinned_col = col.ops.remove_consecutive_duplicates_across()
"""



remove_outliers = register_pipeline(
    steps=[
        (functional_stats.detect_outliers, {}),
        (filters.eq, {"value": 0}),
        (filter_rows, {})
    ],
    domain="core",
    name="remove_outliers",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "vals": ("column", str),
        "window_size": (int, 3),
        "threshold": (float, 0.5),
        "edge_handling": (str, "asymmetric"),
        "scale_factor": (float, 1.0),
    }
)
remove_outliers.__doc__ = """特定の基準（外れ値検知ロジック）に基づいて外れ値と判定された行を除外します。

    Args:
        collection (ColumnCollection): データコレクション
        column (str): 外れ値判定の対象となるカラム名
        window_size (int, optional): 移動窓のサイズ. Defaults to 3.
        threshold (float, optional): 外れ値と判定する閾値. Defaults to 0.5.
        edge_handling (str, optional): 端の処理手法. Defaults to "asymmetric".
        min_abs_value (float, optional): 最小絶対値. Defaults to 1e-10.
        scale_factor (float, optional): スケールファクター. Defaults to 1.0.

    Returns:
        ColumnCollection: 外れ値が除外された新しいコレクション
        
    Examples:
        >>> clean_col = col.ops.remove_outliers("変位", threshold=0.3)
"""


filter_by_condition = register_functional(
    filters.filter_by_condition,
    domain="core",
    name="filter_by_condition",
    filter_rows=True,
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "vals": ("column", str)
    }
)
filter_by_condition.__doc__ = """コールバック関数を使って、指定カラムの値に対するカスタム条件で行を抽出します。

    Args:
        collection (ColumnCollection): データコレクション
        column (str): 条件判定の対象となるカラム名
        condition (Callable[[np.ndarray], np.ndarray]): 真偽値配列を返す条件関数
        
    Returns:
        ColumnCollection: 条件関数がTrueを返した行のみを含む新しいコレクション
        
    Examples:
        >>> # 荷重が50以上の行だけを抽出
        >>> high_load_col = col.ops.filter_by_condition("荷重", lambda x: x >= 50)
"""


remove_steps = register_functional(
    filters.remove_steps_mask,
    domain="core",
    name="remove_steps",
    filter_rows=True,
    inject_step_values={},
    signature_override={
        # step_values injected, steps passed
    }
)
remove_steps.__doc__ = """指定されたステップ値のリストに一致する行を除外します。

    Args:
        collection (ColumnCollection): データコレクション
        steps (List[float] | np.ndarray): 除外したいステップ値のリスト
        
    Returns:
        ColumnCollection: 指定したステップが除外された新しいコレクション
        
    Examples:
        >>> filtered_col = col.ops.remove_steps(steps=[1.0, 2.0, 3.0])
"""


# ---------------------------------------------------------
# 検索操作 (search.pyから統合)
# ---------------------------------------------------------

search_by_value = register_functional(
    filters.search,
    domain="core",
    name="search_by_value",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "values": ("values", Any),
    }
)
search_by_value.__doc__ = """指定された値に一致するデータのインデックスリストを返します（抽出は行いません）

    Args:
        collection (ColumnCollection): データコレクション
        values (str | np.ndarray): 検索対象のカラム名または配列
        value (Any): 検索する値
        tolerance (float, optional): 許容誤差. Defaults to None.
        
    Returns:
        np.ndarray: 一致したインデックスの配列
        
    Examples:
        >>> indices = col.ops.search_by_value("状態", "エラー")
"""


search_by_range = register_functional(
    filters.search_range,
    domain="core",
    name="search_by_range",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "values": ("vals", Any),
    }
)
search_by_range.__doc__ = """指定したカラムの値が一定の範囲に収まるインデックスリストを返します

    Args:
        collection (ColumnCollection): データコレクション
        vals (str | np.ndarray): 検索対象のカラム名または配列
        min (float, optional): 最小値. Defaults to None.
        max (float, optional): 最大値. Defaults to None.
        inclusive (bool, optional): 境界値を含むか. Defaults to True.
        
    Returns:
        np.ndarray: 範囲内に収まるインデックスの配列
        
    Examples:
        >>> indices = col.ops.search_by_range("荷重", min=10.0, max=50.0)
"""


def _search_step_metadata(args, kwargs, result):
    min_val = kwargs.get("min", args[0] if len(args) > 0 else None)
    max_val = kwargs.get("max", args[1] if len(args) > 1 else None)
    inclusive = kwargs.get("inclusive", True)
    by_step_value = kwargs.get("by_step_value", True)
    
    return {
        "operation": "search_by_step_range",
        "by_step_value": by_step_value,
        "min": min_val,
        "max": max_val,
        "inclusive": inclusive,
    }


search_by_step_range = register_functional(
    filters.search_step_range,
    domain="core",
    name="search_by_step_range",
    inject_step_values={"cast_to_numpy": True},
    inject_metadata=_search_step_metadata,
)
search_by_step_range.__doc__ = """ステップ値が一定の範囲に収まるインデックスリストを返します

    Args:
        collection (ColumnCollection): データコレクション
        min (float, optional): 最小ステップ値. Defaults to None.
        max (float, optional): 最大ステップ値. Defaults to None.
        inclusive (bool, optional): 境界値を含むか. Defaults to True.
        compare_mode (str, optional): 比較モード ("value", "index"). Defaults to "value".
        by_step_value (bool, optional): 基準軸としてステップ値を使うか. Defaults to True.
        
    Returns:
        np.ndarray: 条件に一致したインデックスの配列
        
    Examples:
        >>> indices = col.ops.search_by_step_range(min=0.0, max=10.0)
"""


search_by_condition = register_functional(
    filters.search_by_condition,
    domain="core",
    name="search_by_condition",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    signature_override={
        "data": ("columns", Optional[List[str]])
    }
)
search_by_condition.__doc__ = """複数のカラムに対して、指定した条件関数を満たすインデックスリストを返します

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 検索対象のカラム名リスト. 未指定時はすべて. Defaults to None.
        condition (Callable[[np.ndarray], np.ndarray]): 真偽値配列を返す条件関数
        mode (str, optional): 判定モード ("any" または "all"). Defaults to "any".
        
    Returns:
        np.ndarray: 一致したインデックスの配列
        
    Examples:
        >>> indices = col.ops.search_by_condition(columns=["荷重"], condition=lambda x: x > 100)
"""


search_missing_values = register_functional(
    filters.search_missing_values,
    domain="core",
    name="search_missing_values",
    inject_columns={"columns_arg": "columns", "cast_to_numpy": True},
    signature_override={
        "data": ("columns", Optional[List[str]])
    }
)
search_missing_values.__doc__ = """欠損値（None/NaN）が含まれるインデックスリストを返します

    Args:
        collection (ColumnCollection): データコレクション
        columns (List[str], optional): 検索対象のカラム名リスト. 未指定時はすべて. Defaults to None.
        mode (str, optional): 判定モード ("any" または "all"). Defaults to "any".
        
    Returns:
        np.ndarray: 欠損値を含むインデックスの配列
        
    Examples:
        >>> nan_indices = col.ops.search_missing_values()
"""


search_top_n = register_functional(
    filters.top_n,
    domain="core",
    name="search_top_n",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    signature_override={
        "values": ("vals", Any),
    }
)
search_top_n.__doc__ = """指定されたカラムから上位または下位N件のインデックスリストを返します

    Args:
        collection (ColumnCollection): データコレクション
        vals (str | np.ndarray): 対象のカラム名または配列
        n (int, optional): 取得件数. Defaults to 5.
        largest (bool, optional): Trueなら大きい順、Falseなら小さい順. Defaults to True.
        
    Returns:
        np.ndarray: 上位（下位）N件のインデックスの配列
        
    Examples:
        >>> top_5_idx = col.ops.search_top_n("荷重", n=5, largest=True)
"""


