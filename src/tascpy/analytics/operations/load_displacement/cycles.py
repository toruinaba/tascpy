"""荷重-変位データのサイクル処理関数"""

from typing import Union, List, Optional
import numpy as np
from ...operations.registry import operation
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.core.column import Column


from ...operations.registry import register_functional
from ...functional.load_displacement.cycles import compute_cycle_markers
from .abstraction import resolve_load_column, resolve_ld_and_cycle_columns

cycle_count = operation(domain="load_displacement")(resolve_load_column(register_functional(
    compute_cycle_markers,
    domain="load_displacement",
    name="cycle_count",
    inject_columns={"num_inputs": 1, "cast_to_numpy": True},
    store_result={"result_naming": "{0}_cycle"},
    signature_override={
        "data": ("column", float),
    }
)))
cycle_count.__doc__ = """荷重データの符号反転に基づいてサイクルをカウントします

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        data (str, optional): 荷重データのカラム名（None時はメタデータから解決）
        step (float, optional): ノイズ除去のための変化判定ステップ幅. Defaults to 0.5.
        
    Returns:
        LoadDisplacementCollection: サイクル番号が追加された新しいコレクション
"""


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
analyze_hysteresis.__doc__ = """各サイクルのヒステリシスエネルギー（面積）と最大/最小荷重・変位を計算します

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        cycle_column (str, optional): サイクル番号のカラム名（None時は自動解決）
        load_column (str, optional): 荷重データのカラム名（None時は自動解決）
        displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
        cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名
        
    Returns:
        LoadDisplacementCollection: サイクルごとの統計量を持つ新しいコレクション
"""

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
analyze_stiffness_degradation.__doc__ = """各サイクルの割線剛性（剛性低下）を評価します

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        cycle_column (str, optional): サイクル番号のカラム名（None時は自動解決）
        load_column (str, optional): 荷重データのカラム名（None時は自動解決）
        displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
        cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名
        
    Returns:
        LoadDisplacementCollection: サイクルごとの割線剛性を持つ新しいコレクション
"""


from ...functional.load_displacement.cycles import compute_peaks_and_valleys
find_peaks_and_valleys = operation(domain="load_displacement")(resolve_load_column(register_functional(
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
)))
find_peaks_and_valleys.__doc__ = """荷重データのピーク（極大値）とバレー（極小値）を検出します

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        data (str, optional): 荷重データのカラム名（None時は自動解決）
        distance (int, optional): 隣接するピーク間の最小距離. Defaults to 1.
        threshold (float, optional): ピークとして認識するための閾値
        prominence (float, optional): 周囲からの最低の突出度
        
    Returns:
        LoadDisplacementCollection: ピーク（1）、バレー（-1）、その他（0）を示すマーカーカラムが追加された新しいコレクション
"""
