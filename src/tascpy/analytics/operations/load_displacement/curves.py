"""荷重-変位データの特殊曲線生成関数"""

from typing import Optional
import numpy as np
from tascpy.domains.load_displacement import LoadDisplacementCollection
from ...operations.registry import operation
from ...operations.abstraction import store_xy_result
from ...functional.load_displacement.curves import (
    compute_skeleton_curve,
    compute_cumulative_curve,
)
from ...functional.load_displacement.cycles import compute_cycle_markers


def _get_cycle_arrays_with_fallback(collection, load_column=None, displacement_column=None, cycle_marker_column=None):
    """collection.get_ld_cycle_arrays() を呼び出し、マーカーが存在しない場合は自動生成する。"""
    try:
        return collection.get_ld_cycle_arrays(
            load_column=load_column,
            displacement_column=displacement_column,
            cycle_marker_column=cycle_marker_column,
        )
    except KeyError:
        ld_info = collection.metadata.get("load_displacement_domain", {})
        load_col = load_column or ld_info.get("load_column", collection.load_column)
        disp_col = displacement_column or ld_info.get("displacement_column", collection.displacement_column)
        loads = np.array(collection[load_col].values)
        disps = np.array(collection[disp_col].values)
        markers = compute_cycle_markers(loads)
        return loads, disps, markers


@operation(domain="load_displacement")
@store_xy_result(name="skeleton_curve")
def create_skeleton_curve(
    collection: LoadDisplacementCollection,
    load_column: Optional[str] = None,
    displacement_column: Optional[str] = None,
    cycle_marker_column: Optional[str] = None,
    has_decrease: bool = False,
    decrease_type: str = "envelope",
) -> LoadDisplacementCollection:
    """荷重-変位データからスケルトン曲線（包絡線）を生成します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        load_column (str, optional): 荷重データのカラム名（None時は自動解決）
        displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
        cycle_marker_column (str, optional): サイクルマーカーカラム名（None時は自動解決）
        has_decrease (bool, optional): 剛性低下を考慮するかどうか. Defaults to False.
        decrease_type (str, optional): 剛性低下の計算手法. Defaults to "envelope".

    Returns:
        LoadDisplacementCollection: スケルトン曲線データが結果として追加された新しいコレクション

    Examples:
        >>> col = col.ops.create_skeleton_curve(has_decrease=True, decrease_type="envelope")
    """
    loads, disps, markers = _get_cycle_arrays_with_fallback(
        collection,
        load_column=load_column,
        displacement_column=displacement_column,
        cycle_marker_column=cycle_marker_column,
    )
    return compute_skeleton_curve(
        loads, disps, markers,
        has_decrease=has_decrease,
        decrease_type=decrease_type,
    )


@operation(domain="load_displacement")
@store_xy_result(name="cumulative_curve")
def create_cumulative_curve(
    collection: LoadDisplacementCollection,
    load_column: Optional[str] = None,
    displacement_column: Optional[str] = None,
    cycle_marker_column: Optional[str] = None,
) -> LoadDisplacementCollection:
    """荷重-変位データから累積塑性変形-荷重曲線を生成します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        load_column (str, optional): 荷重データのカラム名（None時は自動解決）
        displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
        cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名

    Returns:
        LoadDisplacementCollection: 累積曲線データが結果として追加された新しいコレクション

    Examples:
        >>> col = col.ops.create_cumulative_curve()
    """
    loads, disps, markers = _get_cycle_arrays_with_fallback(
        collection,
        load_column=load_column,
        displacement_column=displacement_column,
        cycle_marker_column=cycle_marker_column,
    )
    return compute_cumulative_curve(loads, disps, markers)
