from typing import Optional, Any, List, Dict
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from tascpy.visualization.plotters.core.plotter import CorePlotter
from tascpy.visualization.functional.load_displacement import plot as ld_plot
from tascpy.analytics.operations.load_displacement.analysis import find_yield_point


class LoadDisplacementPlotter(CorePlotter):
    """LoadDisplacementドメイン特化のデータ可視化を提供するPlotterクラス
    
    LoadDisplacementCollectionからドメイン特有のメタデータ（荷重・変位カラム名）
    を抽出して適宜デフォルト値として利用しつつ、純粋配列を描画関数へ渡します。
    """

    def __init__(self, collection):
        super().__init__(collection)
        self._collection = collection

    def _resolve_ld_columns(
        self, x_column: Optional[str] = None, y_column: Optional[str] = None
    ) -> tuple[str, str]:
        """指定がない場合はLoadDisplacementCollectionのデフォルトカラムを返します"""
        x_col = x_column
        y_col = y_column
        if y_col is None and hasattr(self._collection, "load_column"):
            y_col = self._collection.load_column
        if x_col is None and hasattr(self._collection, "displacement_column"):
            x_col = self._collection.displacement_column

        if x_col is None or y_col is None:
            raise ValueError("x_column or y_column is not provided and defaults could not be found.")

        return x_col, y_col

    def __call__(self, *args, **kwargs) -> Axes:
        """PlotProxyとの互換性のため直接呼び出し時はplot_load_displacementを実行します"""
        return self.plot_load_displacement(*args, **kwargs)

    def plot_load_displacement(
        self,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        ax: Optional[Axes] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        **kwargs
    ) -> Axes:
        """荷重-変位曲線をプロットします
        
        Args:
            x_column: 変位カラム名（省略時はデフォルト）
            y_column: 荷重カラム名（省略時はデフォルト）
            ax: 描画先のAxes
            x_label: X軸のラベル
            y_label: Y軸のラベル
            **kwargs: matplotlibのplot関数に渡す追加引数
            
        Returns:
            Axes: 描画されたAxes
        """
        x_col, y_col = self._resolve_ld_columns(x_column, y_column)
        x_vals, auto_x_label = self._extract_axis(x_col)
        y_vals, auto_y_label = self._extract_axis(y_col)

        return ld_plot.plot_load_displacement(
            x_values=x_vals,
            y_values=y_vals,
            x_label=x_label if x_label is not None else auto_x_label,
            y_label=y_label if y_label is not None else auto_y_label,
            ax=ax,
            **kwargs
        )

    def plot_skeleton_curve(
        self,
        skeleton_x: Optional[np.ndarray] = None,
        skeleton_y: Optional[np.ndarray] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        ax: Optional[Axes] = None,
        plot_original: bool = True,
        original_kwargs: Optional[Dict[str, Any]] = None,
        skeleton_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Axes:
        """スケルトン曲線をプロットします
        
        Args:
            skeleton_x: スケルトン曲線の変位配列（省略時はコレクション内から抽出）
            skeleton_y: スケルトン曲線の荷重配列（省略時はコレクション内から抽出）
            x_column: 元データの変位カラム名
            y_column: 元データの荷重カラム名
        """
        if skeleton_x is None or skeleton_y is None:
            try:
                res = self._collection.results.get("skeleton_curve")
                if res is not None:
                    curve_info = res.to_dict()
                    skeleton_x = np.array(curve_info["data"]["x"])
                    skeleton_y = np.array(curve_info["data"]["y"])
                else:
                    curve_info = self._collection["curves"]["skeleton_curve"]
                    if "data" in curve_info:
                        skeleton_x = np.array(curve_info["data"]["x"])
                        skeleton_y = np.array(curve_info["data"]["y"])
                    elif "columns" in curve_info:
                        x_col = curve_info["columns"]["x"]
                        y_col = curve_info["columns"]["y"]
                        skeleton_x = np.array(self._collection[x_col].values)
                        skeleton_y = np.array(self._collection[y_col].values)
            except (KeyError, TypeError) as e:
                raise ValueError("skeleton_x and skeleton_y must be provided or exist in collection curves.") from e

        if plot_original:
            try:
                x_col, y_col = self._resolve_ld_columns(x_column, y_column)
                x_vals, auto_x_label = self._extract_axis(x_col)
                y_vals, auto_y_label = self._extract_axis(y_col)
            except ValueError:
                x_vals, y_vals = None, None
                auto_x_label, auto_y_label = "Displacement", "Load"
        else:
            x_vals, y_vals = None, None
            auto_x_label, auto_y_label = x_label or "Displacement", y_label or "Load"

        return ld_plot.plot_skeleton_curve(
            skeleton_x=skeleton_x,
            skeleton_y=skeleton_y,
            x_values=x_vals,
            y_values=y_vals,
            x_label=x_label if x_label is not None else auto_x_label,
            y_label=y_label if y_label is not None else auto_y_label,
            ax=ax,
            original_kwargs=original_kwargs,
            skeleton_kwargs=skeleton_kwargs,
        )

    def plot_cumulative_curve(
        self,
        cumulative_x: Optional[np.ndarray] = None,
        cumulative_y: Optional[np.ndarray] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        ax: Optional[Axes] = None,
        plot_original: bool = True,
        original_kwargs: Optional[Dict[str, Any]] = None,
        cumulative_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Axes:
        """累積曲線をプロットします"""
        if cumulative_x is None or cumulative_y is None:
            try:
                res = self._collection.results.get("cumulative_curve")
                if res is not None:
                    curve_info = res.to_dict()
                    cumulative_x = np.array(curve_info["data"]["x"])
                    cumulative_y = np.array(curve_info["data"]["y"])
                else:
                    curve_info = self._collection["curves"]["cumulative_curve"]
                    if "data" in curve_info:
                        cumulative_x = np.array(curve_info["data"]["x"])
                        cumulative_y = np.array(curve_info["data"]["y"])
                    elif "columns" in curve_info:
                        x_col = curve_info["columns"]["x"]
                        y_col = curve_info["columns"]["y"]
                        cumulative_x = np.array(self._collection[x_col].values)
                        cumulative_y = np.array(self._collection[y_col].values)
            except (KeyError, TypeError) as e:
                raise ValueError("cumulative_x and cumulative_y must be provided or exist in collection curves.") from e

        if plot_original:
            try:
                x_col, y_col = self._resolve_ld_columns(x_column, y_column)
                x_vals, auto_x_label = self._extract_axis(x_col)
                y_vals, auto_y_label = self._extract_axis(y_col)
            except ValueError:
                x_vals, y_vals = None, None
                auto_x_label, auto_y_label = "Displacement", "Load"
        else:
            x_vals, y_vals = None, None
            auto_x_label, auto_y_label = x_label or "Displacement", y_label or "Load"

        return ld_plot.plot_cumulative_curve(
            cumulative_x=cumulative_x,
            cumulative_y=cumulative_y,
            x_values=x_vals,
            y_values=y_vals,
            x_label=x_label if x_label is not None else auto_x_label,
            y_label=y_label if y_label is not None else auto_y_label,
            ax=ax,
            original_kwargs=original_kwargs,
            cumulative_kwargs=cumulative_kwargs,
        )

    def plot_yield_point(
        self,
        yield_disp: Optional[float] = None,
        yield_load: Optional[float] = None,
        yield_method: str = "unknown",
        initial_slope: float = 1.0,
        yield_parameters: Optional[Dict[str, Any]] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        ax: Optional[Axes] = None,
        plot_original_data: bool = True,
        plot_initial_slope: bool = True,
        plot_offset_line: bool = True,
        result_prefix: str = "yield",
        **kwargs
    ) -> Axes:
        """降伏点解析結果をプロットします"""
        if yield_disp is None or yield_load is None:
            yp = None
            if hasattr(self._collection, "results"):
                yp = self._collection.results.get(f"{result_prefix}_point")

            if yp is None and hasattr(self._collection, "__getitem__"):
                try:
                    yp = self._collection[f"analysis.{result_prefix}_point"]
                except KeyError:
                    pass
            
            if yp is None:
                raise ValueError("コレクションに降伏点の解析結果が含まれていません")

            yield_disp = yp.x
            yield_load = yp.y
            md = yp.metadata or {}
            
            if yield_method == "unknown" and "method" in md:
                yield_method = md["method"]
            if initial_slope == 1.0 and "initial_slope" in md:
                initial_slope = md["initial_slope"]
            if yield_parameters is None and "parameters" in md:
                yield_parameters = md["parameters"]

        if plot_original_data:
            try:
                x_col, y_col = self._resolve_ld_columns(x_column, y_column)
                x_vals, auto_x_label = self._extract_axis(x_col)
                y_vals, auto_y_label = self._extract_axis(y_col)
            except ValueError:
                x_vals, y_vals = None, None
                auto_x_label, auto_y_label = "Displacement", "Load"
        else:
            x_vals, y_vals = None, None
            auto_x_label, auto_y_label = x_label or "Displacement", y_label or "Load"

        return ld_plot.plot_yield_point(
            yield_disp=yield_disp,
            yield_load=yield_load,
            yield_method=yield_method,
            initial_slope=initial_slope,
            yield_parameters=yield_parameters,
            x_values=x_vals,
            y_values=y_vals,
            x_label=x_label if x_label is not None else auto_x_label,
            y_label=y_label if y_label is not None else auto_y_label,
            ax=ax,
            plot_original_data=plot_original_data,
            plot_initial_slope=plot_initial_slope,
            plot_offset_line=plot_offset_line,
            result_prefix=result_prefix,
            **kwargs
        )

    def plot_yield_analysis_details(
        self,
        yield_disp: Optional[float] = None,
        yield_load: Optional[float] = None,
        yield_method: str = "unknown",
        initial_slope: float = 1.0,
        yield_parameters: Optional[Dict[str, Any]] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        ax: Optional[Axes] = None,
        plot_original: bool = True,
        original_kwargs: Optional[Dict[str, Any]] = None,
        yield_point_kwargs: Optional[Dict[str, Any]] = None,
        lines_kwargs: Optional[Dict[str, Any]] = None,
        result_prefix: str = "yield",
        **kwargs
    ) -> Axes:
        """詳細な降伏点解析内容をプロットします"""
        if yield_disp is None or yield_load is None:
            yp = None
            if hasattr(self._collection, "results"):
                yp = self._collection.results.get(f"{result_prefix}_point")

            if yp is None and hasattr(self._collection, "__getitem__"):
                try:
                    yp = self._collection[f"analysis.{result_prefix}_point"]
                except KeyError:
                    pass
            
            if yp is None:
                raise ValueError("コレクションに降伏点の解析結果が含まれていません")

            yield_disp = yp.x
            yield_load = yp.y
            md = yp.metadata or {}
            
            if yield_method == "unknown" and "method" in md:
                yield_method = md["method"]
            if initial_slope == 1.0 and "initial_slope" in md:
                initial_slope = md["initial_slope"]
            if yield_parameters is None and "parameters" in md:
                yield_parameters = md["parameters"]

        if plot_original:
            try:
                x_col, y_col = self._resolve_ld_columns(x_column, y_column)
                x_vals, auto_x_label = self._extract_axis(x_col)
                y_vals, auto_y_label = self._extract_axis(y_col)
            except ValueError:
                x_vals, y_vals = None, None
                auto_x_label, auto_y_label = "Displacement", "Load"
        else:
            x_vals, y_vals = None, None
            auto_x_label, auto_y_label = x_label or "Displacement", y_label or "Load"
            
        return ld_plot.plot_yield_analysis_details(
            yield_disp=yield_disp,
            yield_load=yield_load,
            yield_method=yield_method,
            initial_slope=initial_slope,
            yield_parameters=yield_parameters,
            x_values=x_vals,
            y_values=y_vals,
            x_label=x_label if x_label is not None else auto_x_label,
            y_label=y_label if y_label is not None else auto_y_label,
            ax=ax,
            **kwargs
        )

    def compare_yield_methods(
        self,
        methods: Optional[List[Dict[str, Any]]] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        ax: Optional[Axes] = None,
        **kwargs
    ) -> Axes:
        """複数の降伏点手法を解析し、比較して表示します"""
        if methods is None:
            methods = [{"method": "offset"}, {"method": "general"}]
            
        yield_results = []
        for params in methods:
            params_copy = params.copy()
            if "result_prefix" in params_copy:
                del params_copy["result_prefix"]

            try:
                res = find_yield_point(self._collection, **params_copy)
                yp = res.results.get("yield_point")
                if yp:
                    yield_results.append({
                        "yield_disp": yp.x,
                        "yield_load": yp.y,
                        "method": yp.metadata.get("method"),
                        "initial_slope": yp.metadata.get("initial_slope"),
                        "parameters": yp.metadata.get("parameters", {})
                    })
            except Exception as e:
                print(f"Failed to find yield point for {params}: {e}")

        try:
            x_col, y_col = self._resolve_ld_columns(x_column, y_column)
            x_vals, auto_x_label = self._extract_axis(x_col)
            y_vals, auto_y_label = self._extract_axis(y_col)
        except ValueError:
            x_vals, y_vals = None, None
            auto_x_label, auto_y_label = "Displacement", "Load"

        return ld_plot.compare_yield_methods(
            yield_results=yield_results,
            x_values=x_vals,
            y_values=y_vals,
            x_label=x_label if x_label is not None else auto_x_label,
            y_label=y_label if y_label is not None else auto_y_label,
            ax=ax,
            **kwargs
        )

    def plot_multiple_curves(
        self,
        curves: List[Dict[str, Any]],
        x_label: str = "Displacement",
        y_label: str = "Load",
        ax: Optional[Axes] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
    ) -> Axes:
        """複数の曲線を指定してプロットします
        
        curves に渡す dict は {"type": "original" | "skeleton" | "cumulative", "kwargs": {...}}
        または明示的に {"x": np.ndarray, "y": np.ndarray, "kwargs": {...}} を指定します。
        """
        curves_data = []
        for curve_def in curves:
            curve_type = curve_def.get("type")
            if "x" in curve_def and "y" in curve_def:
                curves_data.append(curve_def)
                continue
                
            item = {"kwargs": curve_def.get("kwargs", {}), "type": curve_type}
            try:
                if curve_type == "original":
                    x_c, y_c = self._resolve_ld_columns(x_column, y_column)
                    x_vals, _ = self._extract_axis(x_c)
                    y_vals, _ = self._extract_axis(y_c)
                    item["x"] = x_vals
                    item["y"] = y_vals
                elif curve_type in ["skeleton", "cumulative"]:
                    curve_info = self._collection["curves"].get(f"{curve_type}_curve")
                    if curve_info is None:
                        res = self._collection.results.get(f"{curve_type}_curve")
                        if res is not None:
                            curve_info = res.to_dict()
                    
                    if curve_info and "data" in curve_info:
                        item["x"] = np.array(curve_info["data"]["x"])
                        item["y"] = np.array(curve_info["data"]["y"])
                    elif curve_info and "columns" in curve_info:
                        x_col = curve_info["columns"]["x"]
                        y_col = curve_info["columns"]["y"]
                        item["x"] = np.array(self._collection[x_col].values)
                        item["y"] = np.array(self._collection[y_col].values)
                    else:
                        print(f"Warning: Data for {curve_type}_curve not found in curves. Skipping.")
                        continue
            except Exception as e:
                print(f"Warning: Could not extract data for type '{curve_type}': {e}")
                continue
                
            curves_data.append(item)

        return ld_plot.plot_multiple_curves(
            curves_data=curves_data,
            x_label=x_label,
            y_label=y_label,
            ax=ax
        )
