"""荷重-変位データの特殊曲線生成関数"""

from ...operations.registry import register_functional
from ...functional.load_displacement.curves import (
    compute_skeleton_curve,
    compute_cumulative_curve,
)
from ...operations.load_displacement.abstraction import resolve_ld_and_cycle_columns

# スケルトン曲線の生成操作
create_skeleton_curve = register_functional(
    compute_skeleton_curve,
    domain="load_displacement",
    name="create_skeleton_curve",
    extra_decorators=[resolve_ld_and_cycle_columns],
    store_xy_result={"name": "skeleton_curve"},
    # We don't use inject_columns because resolve_ld_and_cycle_columns handles it already and passes arrays directly.
    # The actual signature of compute_skeleton_curve is (loads, displacements, markers, has_decrease, decrease_type).
    # However, store_xy_result wraps this. The error `TypeError: compute_cumulative_curve() takes 3 positional arguments but 4 were given`
    # indicates we might be passing `*args` that shouldn't be passed. Let's see the error again.
    signature_override={
         "has_decrease": (bool, False),
         "decrease_type": (str, "envelope"),
         "load_column": (str, None),
         "displacement_column": (str, None),
         "cycle_marker_column": (str, None)
    }
)

# 累積塑性変形-荷重曲線の生成操作
create_cumulative_curve = register_functional(
    compute_cumulative_curve,
    domain="load_displacement",
    name="create_cumulative_curve",
    extra_decorators=[resolve_ld_and_cycle_columns],
    store_xy_result={"name": "cumulative_curve"},
)
