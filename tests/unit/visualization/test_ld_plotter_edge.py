import pytest
import numpy as np
from unittest.mock import patch
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.core.result import XYSeriesResult, PointResult
from tascpy.visualization.plotters.load_displacement.plotter import LoadDisplacementPlotter


@pytest.fixture
def empty_collection():
    return ColumnCollection({"C1": [1.0]}, step=[1])


@pytest.fixture
def result_collection():
    """荷重・変位列の指定はないが、解析結果を持つコレクション"""
    col = ColumnCollection({"X": [1.0, 2.0], "Y": [2.0, 4.0]}, step=[1, 2])
    col = col.with_result(XYSeriesResult("skeleton_curve", Column("x", [1.0, 2.0]), Column("y", [2.0, 4.0])))
    col = col.with_result(XYSeriesResult("cumulative_curve", Column("x", [1.0, 2.0]), Column("y", [2.0, 4.0])))
    col = col.with_result(PointResult("yield_point", 1.5, 3.0,
                                      metadata={"method": "mocked", "initial_slope": 2.0, "parameters": {"a": 1}}))
    return col


def test_resolve_ld_columns_error(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with pytest.raises(ValueError, match="x_column or y_column is not provided"):
        plotter._resolve_ld_columns()


def test_plot_skeleton_curve_from_results(result_collection):
    plotter = LoadDisplacementPlotter(result_collection)
    with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_skeleton_curve") as mock_plot:
        plotter.plot_skeleton_curve(plot_original=False)
        mock_plot.assert_called_once()
        np.testing.assert_array_equal(mock_plot.call_args[1]["skeleton_x"], [1.0, 2.0])


def test_plot_skeleton_curve_error(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with pytest.raises(ValueError):
        plotter.plot_skeleton_curve()


def test_plot_skeleton_curve_original_fallback(result_collection):
    plotter = LoadDisplacementPlotter(result_collection)
    with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_skeleton_curve") as mock_plot:
        # 荷重・変位列が解決できないため元データは描画されない
        plotter.plot_skeleton_curve(plot_original=True)
        kwargs = mock_plot.call_args[1]
        assert kwargs["x_values"] is None
        assert kwargs["x_label"] == "Displacement"


def test_plot_cumulative_curve_from_results(result_collection):
    plotter = LoadDisplacementPlotter(result_collection)
    with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_cumulative_curve") as mock_plot:
        plotter.plot_cumulative_curve(plot_original=False)
        mock_plot.assert_called_once()
        np.testing.assert_array_equal(mock_plot.call_args[1]["cumulative_y"], [2.0, 4.0])


def test_plot_cumulative_curve_error(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with pytest.raises(ValueError):
        plotter.plot_cumulative_curve()


def test_plot_cumulative_curve_original_fallback(result_collection):
    plotter = LoadDisplacementPlotter(result_collection)
    with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_cumulative_curve") as mock_plot:
        plotter.plot_cumulative_curve(plot_original=True)
        assert mock_plot.call_args[1]["x_values"] is None


def test_plot_yield_point_from_results(result_collection):
    plotter = LoadDisplacementPlotter(result_collection)
    with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_yield_point") as mock_plot:
        plotter.plot_yield_point(plot_original_data=False)
        kwargs = mock_plot.call_args[1]
        assert kwargs["yield_disp"] == 1.5
        assert kwargs["yield_method"] == "mocked"
        assert kwargs["initial_slope"] == 2.0


def test_plot_yield_point_error(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with pytest.raises(ValueError):
        plotter.plot_yield_point()


def test_plot_yield_point_original_fallback(result_collection):
    plotter = LoadDisplacementPlotter(result_collection)
    with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_yield_point") as mock_plot:
        plotter.plot_yield_point(plot_original_data=True)
        assert mock_plot.call_args[1]["x_values"] is None


def test_plot_yield_analysis_details_error(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with pytest.raises(ValueError):
        plotter.plot_yield_analysis_details()


def test_compare_yield_methods_fallback(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.compare_yield_methods") as mock_plot:
        # 汎用コレクションには find_yield_point がないため、結果は空になる
        plotter.compare_yield_methods(methods=[{"method": "test"}])
        kwargs = mock_plot.call_args[1]
        assert kwargs["yield_results"] == []
        assert kwargs["x_values"] is None


def test_plot_multiple_curves_complex(result_collection):
    plotter = LoadDisplacementPlotter(result_collection)
    curves = [
        {"x": np.array([1]), "y": np.array([2])},
        {"type": "original"},  # 荷重・変位列がないためスキップ
        {"type": "skeleton"},
        {"type": "cumulative"},
        {"type": "unknown"},
    ]
    with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_multiple_curves") as mock_plot:
        plotter.plot_multiple_curves(curves)
        curves_data = mock_plot.call_args[1]["curves_data"]
        # 明示 xy + skeleton + cumulative + unknown（original はスキップ）
        assert len(curves_data) == 4
        assert "original" not in [c.get("type") for c in curves_data]
