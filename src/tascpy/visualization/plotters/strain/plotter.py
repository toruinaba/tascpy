from typing import Optional, Any
from matplotlib.axes import Axes

from tascpy.visualization.plotters.core.plotter import CorePlotter
from tascpy.visualization.functional.strain import plot as strain_plot


class StrainPlotter(CorePlotter):
    """ひずみドメイン特化の可視化クラス
    
    CorePlotterの機能に加え、ロゼット主ひずみベクトルの描画等
    ひずみ解析特有の可視化機能を提供します。
    """
    
    def plot_rosette_vectors(
        self,
        rosette_name: str,
        step_index: int = 0,
        scale: float = 1.0,
        ax: Optional[Axes] = None
    ) -> Axes:
        """主ひずみベクトルをプロットします"""
        # ロゼット情報からカラム名を推定 (strain.visualization と共通)
        prefix = rosette_name
        cols = {
            "e1": f"{prefix}_e1",
            "e2": f"{prefix}_e2",
            "theta": f"{prefix}_theta"
        }
        
        for key, col in cols.items():
            if col not in self._collection.columns:
                raise ValueError(f"計算済みカラム '{col}' が見つかりません。先に calculate_rosette_strains を実行してください。")

        # データ取得
        try:
            val_e1 = self._collection[cols["e1"]].values[step_index]
            val_e2 = self._collection[cols["e2"]].values[step_index]
            val_theta = self._collection[cols["theta"]].values[step_index]
            
            # 座標取得
            x, y, z = self._collection.get_column_coordinates(cols["e1"])
            if x is None or y is None:
                 rosette_info = self._collection.get_rosette(rosette_name)
                 if rosette_info and "columns" in rosette_info:
                     x, y, z = self._collection.get_column_coordinates(rosette_info["columns"][0])
        except IndexError:
            raise ValueError(f"Step index {step_index} is out of range.")
            
        if x is None or y is None:
            raise ValueError(f"ロゼット '{rosette_name}' の座標情報が取得できませんでした。")

        return strain_plot.plot_rosette_vectors(
            x=x,
            y=y,
            e1=val_e1,
            e2=val_e2,
            theta=val_theta,
            rosette_name=rosette_name,
            step_index=step_index,
            scale=scale,
            ax=ax
        )
        
    def iplot_rosette_vectors(
        self,
        rosette_name: str,
        step_index: int = 0,
        scale: float = 1.0,
        fig: Optional[Any] = None
    ) -> Any:
        """主ひずみベクトルをPlotlyでインタラクティブにプロットします"""
        prefix = rosette_name
        cols = {
            "e1": f"{prefix}_e1",
            "e2": f"{prefix}_e2",
            "theta": f"{prefix}_theta"
        }
        
        # データ取得
        try:
            val_e1 = self._collection[cols["e1"]].values[step_index]
            val_e2 = self._collection[cols["e2"]].values[step_index]
            val_theta = self._collection[cols["theta"]].values[step_index]
            
            # 座標取得
            x, y, z = self._collection.get_column_coordinates(cols["e1"])
            if x is None or y is None:
                 rosette_info = self._collection.get_rosette(rosette_name)
                 if rosette_info and "columns" in rosette_info:
                     x, y, z = self._collection.get_column_coordinates(rosette_info["columns"][0])
        except (IndexError, KeyError, ValueError) as e:
            raise ValueError(f"Data extraction failed for rosette '{rosette_name}' at step {step_index}: {e}")

        if x is None or y is None:
            raise ValueError(f"ロゼット '{rosette_name}' の座標情報が取得できませんでした。")
            
        return strain_plot.iplot_rosette_vectors(
            x=x,
            y=y,
            e1=val_e1,
            e2=val_e2,
            theta=val_theta,
            rosette_name=rosette_name,
            step_index=step_index,
            scale=scale,
            fig=fig
        )
