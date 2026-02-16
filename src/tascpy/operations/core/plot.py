"""プロットに関する操作モジュール"""

from typing import Optional, Union, List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np # Added numpy

# 日本語フォントサポート
try:
    import japanize_matplotlib

    # マイナス記号を正しく表示するための設定
    mpl.rcParams["axes.unicode_minus"] = False
except ImportError:
    print(
        "警告: japanize_matplotlib をインポートできません。日本語が正しく表示されない可能性があります。"
    )

from ...operations.registry import operation, register_functional
from ..abstraction import inject_plot_data, inject_columns
# detect_outliers is no longer needed here as it is handled in functional.plot
# from .stats import detect_outliers
from .filters import filter_by_value
from ...functional import plot as functional_plot


plot = register_functional(
    functional_plot.plot,
    domain="core",
    name="plot",
    # No store_result needed (returns Axes)
    # inject_plot_data replaces arguments, so signature override might be tricky
    # But inject_plot_data calls inner with (x_values, y_values, x_label, y_label, title, ax=None, **kwargs)
    # This matches functional_plot.plot signature.
    extra_decorators=[inject_plot_data(x_arg="x_column", y_arg="y_column")]
)


visualize_outliers = register_functional(
    functional_plot.visualize_outliers,
    domain="core",
    name="visualize_outliers",
    extra_decorators=[inject_plot_data(x_arg="x_column", y_arg="column", positional_order=["column", "x_column"])]
)


plot_const_x = register_functional(
    functional_plot.plot_const_x,
    domain="core",
    name="plot_const_x",
    # inject_columns extracts columns into 'y_data' dict
    inject_columns={"columns_arg": "y_columns", "cast_to_numpy": True, "columns_arg_pos": 1}, 
    signature_override={
        "y_data": ("y_columns", List[str]),
        "x_values": (List[float], None) # Assuming x_values is passed explicitly
    }
)



iplot = register_functional(
    functional_plot.iplot,
    domain="core",
    name="iplot",
    extra_decorators=[inject_plot_data(x_arg="x_column", y_arg="y_column")]
)

