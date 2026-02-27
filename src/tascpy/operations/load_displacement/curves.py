"""荷重-変位データの特殊曲線生成関数"""

from typing import Optional, Tuple
import numpy as np
from ...core.collection import ColumnCollection
from ...operations.registry import operation
from ...operations.abstraction import store_xy_result
from ...functional.load_displacement.curves import compute_skeleton_curve, compute_cumulative_curve
from ...plugins.load_displacement import cycle_count


@operation(domain="load_displacement")
@store_xy_result(name="skeleton_curve")
def create_skeleton_curve(
    collection: ColumnCollection,
    load_column: Optional[str] = None,
    displacement_column: Optional[str] = None,
    cycle_marker_column: Optional[str] = None,
    has_decrease: bool = False,
    decrease_type: str = "envelope"
) -> Tuple[np.ndarray, np.ndarray, dict]:
    ld_info = collection.metadata.get("load_displacement_domain", {})
    load_col = load_column or ld_info.get("load_column", "load")
    disp_col = displacement_column or ld_info.get("displacement_column", "displacement")
    marker_col = cycle_marker_column or ld_info.get("cycle_marker_column", "cycle_marker")
    
    loads = np.array(collection[load_col].values)
    disps = np.array(collection[disp_col].values)
    
    try:
        markers = np.array(collection[marker_col].values)
    except KeyError:
        markers = np.array(cycle_count(loads.tolist()))
    
    d_ske, p_ske = compute_skeleton_curve(
        loads=loads,
        displacements=disps,
        markers=markers,
        has_decrease=has_decrease,
        decrease_type=decrease_type
    )
    
    # store_xy_result expects (x, y, meta)
    # where x is displacement, y is load
    return np.array(d_ske), np.array(p_ske), {}


@operation(domain="load_displacement")
@store_xy_result(name="cumulative_curve")
def create_cumulative_curve(
    collection: ColumnCollection,
    load_column: Optional[str] = None,
    displacement_column: Optional[str] = None,
    cycle_marker_column: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    ld_info = collection.metadata.get("load_displacement_domain", {})
    load_col = load_column or ld_info.get("load_column", "load")
    disp_col = displacement_column or ld_info.get("displacement_column", "displacement")
    marker_col = cycle_marker_column or ld_info.get("cycle_marker_column", "cycle_marker")
    
    loads = np.array(collection[load_col].values)
    disps = np.array(collection[disp_col].values)
    
    try:
        markers = np.array(collection[marker_col].values)
    except KeyError:
        markers = np.array(cycle_count(loads.tolist()))
    
    d_cum, p_cum = compute_cumulative_curve(
        loads=loads,
        displacements=disps,
        markers=markers
    )
    
    # store_xy_result expects (x, y, meta)
    return np.array(d_cum), np.array(p_cum), {}
