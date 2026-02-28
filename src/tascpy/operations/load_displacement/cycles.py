"""荷重-変位データのサイクル処理関数"""

from typing import Union, List, Optional
import numpy as np
from ...operations.registry import operation
from ...domains.load_displacement import LoadDisplacementCollection
from ...core.column import Column


from ...operations.registry import register_functional
from ...functional.load_displacement.cycles import compute_cycle_markers
from .abstraction import resolve_load_column, resolve_ld_and_cycle_columns

cycle_count = resolve_load_column(register_functional(
    compute_cycle_markers,
    domain="load_displacement",
    name="cycle_count",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    store_result={"result_naming": "{0}_cycle"},
    signature_override={
        "data": ("column", float),
        "step": (float, 0.5)
    }
))


@operation(domain="load_displacement")
def split_by_cycles(
    collection: LoadDisplacementCollection, cycle_column: Optional[str] = None
) -> List[LoadDisplacementCollection]:
    """サイクル番号ごとにデータを分割

    データをサイクル番号ごとに分割し、各サイクルの
    荷重-変位コレクションのリストを返します。

    Args:
        collection: 荷重-変位コレクション
        cycle_column: サイクル番号を含む列名（指定がない場合は自動検出/生成）

    Returns:
        List[LoadDisplacementCollection]: サイクルごとに分割されたコレクションのリスト
    """
    # サイクル列の特定または作成
    if cycle_column is None:
        # 既存のサイクル列を探す
        for col_name in collection.columns:
            if "cycle" in col_name.lower():
                cycle_column = col_name
                break

        # 見つからない場合は荷重列に対してcycle_countを実行
        if cycle_column is None:
            temp_result = cycle_count(collection)
            cycle_column = [
                c for c in temp_result.columns if c not in collection.columns
            ][0]
            collection = temp_result

    # サイクルで分割
    from ...operations.core.select import split_by_integers

    return split_by_integers(collection, collection[cycle_column].values)


def _calculate_polygon_area(x: np.ndarray, y: np.ndarray) -> float:
    """多角形の面積を計算（靴紐の公式）
    
    Args:
        x: X座標配列
        y: Y座標配列
        
    Returns:
        float: 面積（絶対値）
    """
    from ...functional.load_displacement.cycles import calculate_polygon_area
    return calculate_polygon_area(x, y)


from ...functional.load_displacement.cycles import compute_energy_and_stats, compute_stiffness_degradation_stats

analyze_hysteresis = register_functional(
    compute_energy_and_stats,
    domain="load_displacement",
    name="analyze_hysteresis",
    extra_decorators=[resolve_ld_and_cycle_columns],
    process_by_group={
        "group_column_arg": "cycle_column",
        "output_columns": [
            {"name": "cycle", "index": 0},
            {"name": "energy", "index": 1, "unit": "J", "metadata": {"description": "Hysteresis loop area"}},
            {"name": "max_load", "index": 2, "inherit_unit_from": "__load__"},
            {"name": "min_load", "index": 3, "inherit_unit_from": "__load__"},
            {"name": "max_disp", "index": 4, "inherit_unit_from": "__disp__"},
            {"name": "min_disp", "index": 5, "inherit_unit_from": "__disp__"},
        ],
        "collection_cls": LoadDisplacementCollection
    },
    signature_override={
        "cycle_column": (str, None),
        "load_column": (str, None),
        "displacement_column": (str, None),
        "cycle_marker_column": (str, None)
    }
)

analyze_stiffness_degradation = register_functional(
    compute_stiffness_degradation_stats,
    domain="load_displacement",
    name="analyze_stiffness_degradation",
    extra_decorators=[resolve_ld_and_cycle_columns],
    process_by_group={
        "group_column_arg": "cycle_column",
        "output_columns": [
            {"name": "cycle", "index": 0},
            {"name": "stiffness", "index": 1, "metadata": {"description": "Secant stiffness"}}
        ],
        "collection_cls": LoadDisplacementCollection
    },
    signature_override={
        "cycle_column": (str, None),
        "load_column": (str, None),
        "displacement_column": (str, None),
        "cycle_marker_column": (str, None)
    }
)


from ...functional.load_displacement.cycles import compute_peaks_and_valleys
find_peaks_and_valleys = resolve_load_column(register_functional(
    compute_peaks_and_valleys,
    domain="load_displacement",
    name="find_peaks_and_valleys",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    store_result={"result_naming": "peak_valley"},
    signature_override={
        "data": ("column", float),
        "distance": (int, 1),
        "threshold": (float, None),
        "prominence": (float, None),
    }
))
