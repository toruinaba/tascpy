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
create_skeleton_curve.__doc__ = """荷重-変位データからスケルトン曲線（包絡線）を生成します

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        load_column (str, optional): 荷重データのカラム名（None時は自動解決）
        displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
        cycle_marker_column (str, optional): サイクルマーカーカラム名（None時は自動解決）
        has_decrease (bool, optional): 剛性低下を考慮するかどうか. Defaults to False.
        decrease_type (str, optional): 剛性低下の計算手法. Defaults to "envelope".
        
    Returns:
        LoadDisplacementCollection: スケルトン曲線データが結果として追加された新しいコレクション
"""

# 累積塑性変形-荷重曲線の生成操作
create_cumulative_curve = register_functional(
    compute_cumulative_curve,
    domain="load_displacement",
    name="create_cumulative_curve",
    extra_decorators=[resolve_ld_and_cycle_columns],
    store_xy_result={"name": "cumulative_curve"},
)
create_cumulative_curve.__doc__ = """荷重-変位データから累積塑性変形-荷重曲線を生成します

    Args:
        collection (LoadDisplacementCollection): 荷重-変位コレクション
        load_column (str, optional): 荷重データのカラム名（None時は自動解決）
        displacement_column (str, optional): 変位データのカラム名（None時は自動解決）
        cycle_marker_column (str, optional): サブサイクル判定用のマーカーカラム名
        
    Returns:
        LoadDisplacementCollection: 累積曲線データが結果として追加された新しいコレクション
"""
