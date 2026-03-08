"""荷重-変位データのサイクル処理関数"""

from typing import Union, List, Optional, Tuple, Dict, Any
import numpy as np
from ...operations.registry import operation
from tascpy.domains.load_displacement import LoadDisplacementCollection
from ...operations.abstraction import inject_columns, store_result, process_by_group
from ...functional.load_displacement.cycles import (
    compute_cycle_markers,
    compute_energy_and_stats,
    compute_stiffness_degradation_stats,
    compute_peaks_and_valleys,
)


def _get_ld_cycle_arrays_with_fallback(collection, load_column=None, displacement_column=None, cycle_marker_column=None):
    """collection.get_ld_cycle_arrays() を呼び出し、マーカーが存在しない場合は cycle_count で自動生成する。"""
    try:
        return collection.get_ld_cycle_arrays(
            load_column=load_column,
            displacement_column=displacement_column,
            cycle_marker_column=cycle_marker_column,
        )
    except KeyError:
        # サイクルマーカーが存在しないため、荷重データから自動生成
        import numpy as np
        ld_info = collection.metadata.get("load_displacement_domain", {})
        load_col = load_column or ld_info.get("load_column", collection.load_column)
        disp_col = displacement_column or ld_info.get("displacement_column", collection.displacement_column)
        loads = np.array(collection[load_col].values)
        disps = np.array(collection[disp_col].values)
        markers = compute_cycle_markers(loads)
        return loads, disps, markers


@operation(domain="load_displacement")
def cycle_count(
    collection: LoadDisplacementCollection,
    column: Optional[str] = None,
    step: float = 0.5,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> LoadDisplacementCollection:
    """荷重データの符号反転に基づいてサイクルをカウントします。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        column (str, optional): 荷重データのカラム名（None時はメタデータから解決）
        step (float, optional): ノイズ除去のための変化判定ステップ幅. Defaults to 0.5.
        result_column (str, optional): 結果カラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        LoadDisplacementCollection: サイクル番号が追加された新しいコレクション

    Examples:
        >>> col = col.ops.cycle_count(step=1.0)
    """
    from tascpy.core.column import NumberColumn

    col_name = column or collection.load_column
    data = np.array(collection[col_name].values)
    cycle_values = compute_cycle_markers(data, step=step)

    # Derive result column name: '{col_name}_cycle', unless overridden
    out_col = result_column or f"{col_name}_cycle"

    result_collection = collection.clone()
    result_collection.columns[out_col] = NumberColumn(
        ch=ch, name=out_col, unit=unit or "", values=cycle_values.tolist()
    )
    return result_collection


@operation(domain="load_displacement")
def split_by_cycles(
    collection: LoadDisplacementCollection, cycle_column: Optional[str] = None
) -> List[LoadDisplacementCollection]:
    """サイクル番号ごとにデータを分割します。

    データをサイクル番号ごとに分割し、各サイクルの
    荷重-変位コレクションのリストを返します。

    Args:
        collection: 荷重-変位コレクション
        cycle_column: サイクル番号を含む列名（指定がない場合は自動検出/生成）

    Returns:
        List[LoadDisplacementCollection]: サイクルごとに分割されたコレクションのリスト

    Examples:
        >>> cycle_list = col.ops.split_by_cycles()
        >>> first_cycle = cycle_list[0]
    """
    if cycle_column is None:
        for col_name in collection.columns:
            if "cycle" in col_name.lower():
                cycle_column = col_name
                break

        if cycle_column is None:
            temp_result = cycle_count(collection)
            cycle_column = [
                c for c in temp_result.columns if c not in collection.columns
            ][0]
            collection = temp_result

    from ...operations.core.select import split_by_integers
    return split_by_integers(collection, collection[cycle_column].values)


def _calculate_polygon_area(x: np.ndarray, y: np.ndarray) -> float:
    """多角形の面積を計算（靴紐の公式）"""
    from ...functional.load_displacement.cycles import calculate_polygon_area
    return calculate_polygon_area(x, y)


@operation(domain="load_displacement")
@process_by_group(
    group_column_arg="cycle_column",
    output_columns=[
        {"name": "cycle", "index": 0},
        {"name": "energy", "index": 1, "unit": "J", "metadata": {"description": "Hysteresis loop area"}},
        {"name": "max_load", "index": 2, "inherit_unit_from": "__load__"},
        {"name": "min_load", "index": 3, "inherit_unit_from": "__load__"},
        {"name": "max_disp", "index": 4, "inherit_unit_from": "__disp__"},
        {"name": "min_disp", "index": 5, "inherit_unit_from": "__disp__"},
    ],
    collection_cls=LoadDisplacementCollection
)
def analyze_hysteresis(
    collection: LoadDisplacementCollection,
    cycle_column: Optional[str] = None,
    load_column: Optional[str] = None,
    displacement_column: Optional[str] = None,
    cycle_marker_column: Optional[str] = None,
) -> Tuple:
    """各サイクルのヒステリシスエネルギー（面積）と最大/最小荷重・変位を計算します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        cycle_column (str, optional): サイクル番号のカラム名（None時は自動解決）
        load_column (str, optional): 荷重データのカラム名（None時は自動解決）
        displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
        cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名

    Returns:
        LoadDisplacementCollection: サイクルごとの統計量を持つ新しいコレクション

    Examples:
        >>> stats_col = col.ops.analyze_hysteresis()
        >>> energy = stats_col["energy"].values
    """
    loads, disps, markers = _get_ld_cycle_arrays_with_fallback(
        collection,
        load_column=load_column,
        displacement_column=displacement_column,
        cycle_marker_column=cycle_marker_column,
    )
    return compute_energy_and_stats(loads, disps, markers)


@operation(domain="load_displacement")
@process_by_group(
    group_column_arg="cycle_column",
    output_columns=[
        {"name": "cycle", "index": 0},
        {"name": "stiffness", "index": 1, "metadata": {"description": "Secant stiffness"}},
    ],
    collection_cls=LoadDisplacementCollection
)
def analyze_stiffness_degradation(
    collection: LoadDisplacementCollection,
    cycle_column: Optional[str] = None,
    load_column: Optional[str] = None,
    displacement_column: Optional[str] = None,
    cycle_marker_column: Optional[str] = None,
) -> Tuple:
    """各サイクルの割線剛性（剛性低下）を評価します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        cycle_column (str, optional): サイクル番号のカラム名（None時は自動解決）
        load_column (str, optional): 荷重データのカラム名（None時は自動解決）
        displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
        cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名

    Returns:
        LoadDisplacementCollection: サイクルごとの割線剛性を持つ新しいコレクション

    Examples:
        >>> stiffness_col = col.ops.analyze_stiffness_degradation()
    """
    loads, disps, markers = _get_ld_cycle_arrays_with_fallback(
        collection,
        load_column=load_column,
        displacement_column=displacement_column,
        cycle_marker_column=cycle_marker_column,
    )
    return compute_stiffness_degradation_stats(loads, disps, markers)


@operation(domain="load_displacement")
@store_result(result_naming="peak_valley")
@inject_columns(num_inputs=1, pass_collection=True)
def find_peaks_and_valleys(
    collection: LoadDisplacementCollection,
    column: Union[str, np.ndarray] = None,
    distance: int = 1,
    threshold: Optional[float] = None,
    prominence: Optional[float] = None,
    result_column: Optional[str] = None,
    unit: Optional[str] = None,
    ch: Optional[str] = None,
    in_place: bool = False,
) -> LoadDisplacementCollection:
    """荷重データのピーク（極大値）とバレー（極小値）を検出します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        column (str, optional): 荷重データのカラム名（None時は自動解決）
        distance (int, optional): 隣接するピーク間の最小距離. Defaults to 1.
        threshold (float, optional): ピークとして認識するための閾値
        prominence (float, optional): 周囲からの最低の突出度
        result_column (str, optional): 結果カラム名. Defaults to None.
        unit (str, optional): 結果の単位. Defaults to None.
        ch (str, optional): 結果のチャネル名. Defaults to None.
        in_place (bool, optional): 元のコレクションを上書きするか. Defaults to False.

    Returns:
        LoadDisplacementCollection: ピーク（1）、バレー（-1）、その他（0）を示すマーカーカラムが追加された新しいコレクション

    Examples:
        >>> col = col.ops.find_peaks_and_valleys(distance=10, prominence=0.5)
    """
    if column is None:
        column = np.array(collection[collection.load_column].values)
    return compute_peaks_and_valleys(column, distance=distance, threshold=threshold)
