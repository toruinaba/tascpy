from typing import TYPE_CHECKING, Any, List, Optional, Sequence, Tuple

import numpy as np
from matplotlib.axes import Axes

from tascpy.core.plot import draw as core_plot

if TYPE_CHECKING:
    from tascpy.core.collection import ColumnCollection


def axis_label(name: str, unit: Optional[str]) -> str:
    """"名前 [単位]"（単位がなければ名前のみ）"""
    return f"{name} [{unit}]" if unit else name


class CorePlotter:
    """コレクションの列を描画するプロッター（`collection.plot`）

    列の値と単位付きの軸ラベルを取り出し、描画関数（tascpy.visualization.functional）に渡します。
    どのメソッドも Axes（iplot は Plotly Figure）を返し、図の表示（plt.show）は呼び出し側で行います。
    X 軸の列を省略した場合は step を使います。
    """

    def __init__(self, collection: "ColumnCollection"):
        self._collection = collection

    def _extract_axis(self, column_name: Optional[str]) -> Tuple[np.ndarray, str]:
        """列の値と軸ラベル（列名が None なら step）"""
        if column_name is None:
            return self._collection.step, "Step"
        column = self._collection[column_name]
        return column.values, axis_label(column.name, column.unit)

    def plot(
        self,
        y_column: str,
        x_column: Optional[str] = None,
        ax: Optional[Axes] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        **kwargs: Any
    ) -> Axes:
        """折れ線グラフ（plot_type="scatter" で散布図）を描画します

        Args:
            y_column: Y 軸の列名
            x_column: X 軸の列名（省略時は step）
            ax: 描画先の Axes（None の場合は新しい図を作成）
            x_label: X 軸のラベル（省略時は "列名 [単位]"）
            y_label: Y 軸のラベル（省略時は "列名 [単位]"）
            **kwargs: 描画関数に渡す追加引数（plot_type, title, color など）

        Examples:
            >>> ax = col.plot.plot("荷重", "変位")
        """
        y_vals, auto_y = self._extract_axis(y_column)
        x_vals, auto_x = self._extract_axis(x_column)
        return core_plot.plot(x_vals, y_vals, x_label=auto_x if x_label is None else x_label,
                              y_label=auto_y if y_label is None else y_label, ax=ax, **kwargs)

    def plot_const_x(
        self,
        x_values: Sequence[float],
        y_columns: List[str],
        row: int = 0,
        ax: Optional[Axes] = None,
        x_label: str = "Position",
        y_label: Optional[str] = None,
        **kwargs: Any
    ) -> Axes:
        """指定した行の各列の値を、列ごとの位置（x_values）に並べて描画します（ひずみ分布など）

        Args:
            x_values: 各列の位置（y_columns と同じ数）
            y_columns: 描画する列名
            row: 描画する行のインデックス（負の値は末尾から）
            ax: 描画先の Axes（None の場合は新しい図を作成）
            x_label: X 軸のラベル
            y_label: Y 軸のラベル（省略時は列の単位がすべて同じなら "Value [単位]"）
            **kwargs: 描画関数に渡す追加引数

        Examples:
            >>> ax = col.plot.plot_const_x([0.0, 50.0, 100.0], ["CH1", "CH2", "CH3"], row=-1)
        """
        n = len(self._collection)
        if not -n <= row < n:
            raise IndexError(f"行インデックス {row} が範囲外です（行数 {n}）")
        columns = [self._collection[name] for name in y_columns]
        if y_label is None:
            units = {c.unit for c in columns}
            y_label = axis_label("Value", units.pop() if len(units) == 1 else None)
        kwargs.setdefault("title", f"{y_label.split(' [')[0]} at step {self._collection.step[row]}")
        return core_plot.plot_const_x({c.name: c[row] for c in columns}, np.asarray(x_values), x_label=x_label,
                                      y_label=y_label, ax=ax, **kwargs)

    def visualize_outliers(
        self,
        column: str,
        x_column: Optional[str] = None,
        ax: Optional[Axes] = None,
        **kwargs: Any
    ) -> Axes:
        """外れ値を検出して色分けして描画します

        Args:
            column: 対象の列名
            x_column: X 軸の列名（省略時は step）
            ax: 描画先の Axes
            **kwargs: 描画関数に渡す追加引数（window_size, threshold など）

        Examples:
            >>> ax = col.plot.visualize_outliers("荷重")
        """
        y_vals, auto_y = self._extract_axis(column)
        x_vals, auto_x = self._extract_axis(x_column)
        return core_plot.visualize_outliers(x_vals, y_vals, x_label=auto_x, y_label=auto_y, ax=ax, **kwargs)

    def iplot(
        self,
        y_column: str,
        x_column: Optional[str] = None,
        fig: Optional[Any] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        **kwargs: Any
    ) -> Any:
        """Plotly でインタラクティブなグラフを描画します（引数の順序は plot と同じ）

        Examples:
            >>> fig = col.plot.iplot("荷重", "変位")
        """
        y_vals, auto_y = self._extract_axis(y_column)
        x_vals, auto_x = self._extract_axis(x_column)
        return core_plot.iplot(x_vals, y_vals, x_label=auto_x if x_label is None else x_label,
                               y_label=auto_y if y_label is None else y_label, fig=fig, **kwargs)
