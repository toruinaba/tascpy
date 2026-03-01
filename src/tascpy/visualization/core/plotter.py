from typing import Optional, Any, Tuple, List, Dict, Union
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from tascpy.visualization.core import plot as core_plot
from tascpy.operations.abstraction import extract_axis_data

class CorePlotter:
    """基本のデータ可視化を提供するPlotterクラス
    
    Collectionオブジェクトを受け取り、そこから明示的にデータを抽出して
    純粋な可視化関数（tascpy.visualization.core.plot）に渡します。
    """
    
    def __init__(self, collection):
        """
        Args:
            collection: 描画対象のColumnCollectionオブジェクト
        """
        self._collection = collection
        
    def _extract_axis(self, column_name: str) -> Tuple[np.ndarray, str]:
        """指定されたカラムから1次元の変位配列とラベル名を抽出します
        
        Args:
            column_name: カラム名
            
        Returns:
            Tuple[np.ndarray, str]: (値の配列、ラベル文字列)
        """
        val_list, name, unit = extract_axis_data(self._collection, column_name)
        label = f"{name} [{unit}]" if unit else name
        return np.array(val_list), label

    def __call__(self, *args, **kwargs) -> Axes:
        """PlotProxyとの互換性のため直接呼び出し時はplotを実行します"""
        return self.plot(*args, **kwargs)

    def plot(
        self,
        y_column: str,
        x_column: Optional[str] = None,
        ax: Optional[Axes] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        **kwargs
    ) -> Axes:
        """2次元の折れ線または散布図をプロットします
        
        Args:
            y_column: Y軸データのカラム名
            x_column: X軸データのカラム名（None時はインデックスを使用）
            ax: 描画先のAxes（Noneの場合は新規作成）
            x_label: X軸のラベル（Noneの場合は自動生成）
            y_label: Y軸のラベル（Noneの場合は自動生成）
            **kwargs: plot関数に渡す追加引数
            
        Returns:
            描画されたAxes
        """
        y_vals, auto_y_label = self._extract_axis(y_column)
        x_vals, auto_x_label = self._extract_axis(x_column)
        
        return core_plot.plot(
            x_values=x_vals,
            y_values=y_vals,
            ax=ax,
            x_label=x_label if x_label is not None else auto_x_label,
            y_label=y_label if y_label is not None else auto_y_label,
            **kwargs
        )

    def plot_const_x(
        self,
        x_values: Union[List[float], np.ndarray],
        y_columns: List[str],
        ax: Optional[Axes] = None,
        x_label: str = "X Values",
        y_label: str = "Values",
        **kwargs
    ) -> Axes:
        """共通のX軸（位置など）に対して複数のY軸データ（センサー値など）をプロットします
        
        Args:
            x_values: 共通のX軸データの配列
            y_columns: Y軸データのカラム名のリスト
            ax: 描画先のAxes
            x_label: X軸のラベル
            y_label: Y軸のラベル
            **kwargs: plot関数に渡す追加引数
            
        Returns:
            描画されたAxes
        """
        x_vals = np.array(x_values)
        
        # Y値はDictにする (core_plot.plot_const_x が Dict[str, np.ndarray] を期待しているため)
        y_data_dict = {}
        for col in y_columns:
            y_vals, label = self._extract_axis(col)
            y_data_dict[label] = y_vals
            
        return core_plot.plot_const_x(
            y_data=y_data_dict,
            x_values=x_vals,
            ax=ax,
            x_label=x_label,
            y_label=y_label,
            **kwargs
        )

    def visualize_outliers(
        self,
        column: str,
        x_column: Optional[str] = None,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> Axes:
        """異常値を検出して可視化します
        
        Args:
            column: 対象データのカラム名
            x_column: X軸データのカラム名
            ax: 描画先のAxes
            **kwargs: 描画用の追加引数 (window_size, threshold 等)
            
        Returns:
            描画されたAxes
        """
        y_vals, auto_y_label = self._extract_axis(column)
        
        if x_column is not None:
            x_vals, auto_x_label = self._extract_axis(x_column)
        else:
            x_vals = np.arange(len(y_vals))
            auto_x_label = "Index"

        # 古いシグネチャからの互換性を処理
        if "method" in kwargs:
            del kwargs["method"]
        if "multiplier" in kwargs:
            kwargs["threshold"] = kwargs.pop("multiplier")
            
        return core_plot.visualize_outliers(
            x_values=x_vals,
            y_values=y_vals,
            x_label=auto_x_label,
            y_label=auto_y_label,
            ax=ax,
            **kwargs
        )

    def iplot(
        self,
        x_column: str,
        y_column: str,
        fig: Optional[Any] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        **kwargs
    ) -> Any:
        """インタラクティブな出力をPlotlyで行います"""
        from tascpy.visualization.core.plot import iplot as core_iplot
        
        x_vals, auto_x_label = self._extract_axis(x_column)
        y_vals, auto_y_label = self._extract_axis(y_column)
        
        return core_iplot(
            x_values=x_vals,
            y_values=y_vals,
            x_label=x_label if x_label is not None else auto_x_label,
            y_label=y_label if y_label is not None else auto_y_label,
            fig=fig,
            **kwargs
        )
