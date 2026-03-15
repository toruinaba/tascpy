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


@operation(domain="load_displacement")
@store_xy_result(name="skeleton_curve")
def create_skeleton_curve(
    collection: LoadDisplacementCollection,
    cycle_marker_column: Optional[str] = None,
    has_decrease: bool = False,
    decrease_type: str = "envelope",
) -> LoadDisplacementCollection:
    """荷重-変位データからスケルトン曲線（包絡線）を生成します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        cycle_marker_column (str, optional): サイクルマーカーカラム名（None時は自動解決）
        has_decrease (bool, optional): 剛性低下を考慮するかどうか. Defaults to False.
        decrease_type (str, optional): 剛性低下の計算手法. Defaults to "envelope".

    Returns:
        LoadDisplacementCollection: スケルトン曲線データが結果として追加された新しいコレクション

    Examples:
        >>> col = col.ops.create_skeleton_curve(has_decrease=True, decrease_type="envelope")
    """
    loads, disps, markers = collection.get_ld_cycle_arrays(
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
    cycle_marker_column: Optional[str] = None,
) -> LoadDisplacementCollection:
    """荷重-変位データから累積塑性変形-荷重曲線を生成します。

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名

    Returns:
        LoadDisplacementCollection: 累積曲線データが結果として追加された新しいコレクション

    Examples:
        >>> col = col.ops.create_cumulative_curve()
    """
    loads, disps, markers = collection.get_ld_cycle_arrays(
        cycle_marker_column=cycle_marker_column,
    )
    return compute_cumulative_curve(loads, disps, markers)
