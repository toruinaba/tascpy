import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step
from tascpy.core.result import XYSeriesResult, PointResult
from tascpy.visualization.plotters.load_displacement.plotter import LoadDisplacementPlotter

@pytest.fixture
def empty_collection():
    return ColumnCollection(step=Step([1]), columns={"C1": NumberColumn(None, "C1", "", [1.0])})

@pytest.fixture
def old_style_collection():
    col = ColumnCollection(step=Step([1, 2]), columns={"X": NumberColumn(None, "X", "", [1.0, 2.0]), "Y": NumberColumn(None, "Y", "", [2.0, 4.0])})
    return col

def getitem_side_effect(orig_getitem):
    def _mock(self, key):
        if key == "curves":
            return {
                "skeleton_curve": {"data": {"x": [1.0, 2.0], "y": [2.0, 4.0]}},
                "cumulative_curve": {"columns": {"x": "X", "y": "Y"}}
            }
        elif key == "analysis.yield_point":
            return PointResult("yield_point", 1.5, 3.0, metadata={"method": "test"})
        return orig_getitem(self, key)
    return _mock

def test_resolve_ld_columns_error(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with pytest.raises(ValueError, match="x_column or y_column is not provided"):
        plotter._resolve_ld_columns()

def test_plot_skeleton_curve_old_format(old_style_collection):
    plotter = LoadDisplacementPlotter(old_style_collection)
    orig_getitem = ColumnCollection.__getitem__
    with patch.object(ColumnCollection, "__getitem__", new=getitem_side_effect(orig_getitem)):
        with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_skeleton_curve") as mock_plot:
            plotter.plot_skeleton_curve(plot_original=False)
            mock_plot.assert_called_once()
            args, kwargs = mock_plot.call_args
            np.testing.assert_array_equal(kwargs["skeleton_x"], [1.0, 2.0])

def test_plot_skeleton_curve_error(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with pytest.raises(ValueError):
        plotter.plot_skeleton_curve()

def test_plot_skeleton_curve_original_fallback(old_style_collection):
    plotter = LoadDisplacementPlotter(old_style_collection)
    orig_getitem = ColumnCollection.__getitem__
    with patch.object(ColumnCollection, "__getitem__", new=getitem_side_effect(orig_getitem)):
        with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_skeleton_curve") as mock_plot:
            # Plot original without telling it what columns to use, will trigger ValueError in resolve
            plotter.plot_skeleton_curve(plot_original=True)
            kwargs = mock_plot.call_args[1]
            assert kwargs["x_values"] is None
            assert kwargs["x_label"] == "Displacement"

def test_plot_cumulative_curve_old_format(old_style_collection):
    plotter = LoadDisplacementPlotter(old_style_collection)
    orig_getitem = ColumnCollection.__getitem__
    with patch.object(ColumnCollection, "__getitem__", new=getitem_side_effect(orig_getitem)):
        with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_cumulative_curve") as mock_plot:
            plotter.plot_cumulative_curve(plot_original=False)
            mock_plot.assert_called_once()
            args, kwargs = mock_plot.call_args
            np.testing.assert_array_equal(kwargs["cumulative_y"], [2.0, 4.0])

def test_plot_cumulative_curve_error(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with pytest.raises(ValueError):
        plotter.plot_cumulative_curve()

def test_plot_cumulative_curve_original_fallback(old_style_collection):
    plotter = LoadDisplacementPlotter(old_style_collection)
    orig_getitem = ColumnCollection.__getitem__
    with patch.object(ColumnCollection, "__getitem__", new=getitem_side_effect(orig_getitem)):
        with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_cumulative_curve") as mock_plot:
            plotter.plot_cumulative_curve(plot_original=True)
            kwargs = mock_plot.call_args[1]
            assert kwargs["x_values"] is None

def test_plot_yield_point_old_structure(old_style_collection):
    plotter = LoadDisplacementPlotter(old_style_collection)
    orig_getitem = ColumnCollection.__getitem__
    
    def mock_get(self, key):
        if key == "analysis.yield_point":
            return PointResult("yield_point", 1.5, 3.0, metadata={"method": "mocked", "initial_slope": 2.0, "parameters": {"a": 1}})
        return orig_getitem(self, key)
        
    with patch.object(ColumnCollection, "__getitem__", new=mock_get):
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

def test_plot_yield_point_original_fallback(old_style_collection):
    plotter = LoadDisplacementPlotter(old_style_collection)
    def mock_get(self, k):
        if k == "analysis.yield_point":
            return PointResult("yp", 1.0, 1.0)
        return ColumnCollection.__getitem__(self, k)
        
    with patch.object(ColumnCollection, "__getitem__", new=mock_get):
        with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_yield_point") as mock_plot:
            plotter.plot_yield_point(plot_original_data=True)
            kwargs = mock_plot.call_args[1]
            assert kwargs["x_values"] is None

def test_plot_yield_analysis_details_error(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with pytest.raises(ValueError):
        plotter.plot_yield_analysis_details()

def test_compare_yield_methods_fallback(empty_collection):
    plotter = LoadDisplacementPlotter(empty_collection)
    with patch("tascpy.visualization.plotters.load_displacement.plotter.find_yield_point", side_effect=ValueError("Test Err")):
        with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.compare_yield_methods") as mock_plot:
            plotter.compare_yield_methods(methods=[{"method": "test"}])
            kwargs = mock_plot.call_args[1]
            assert kwargs["yield_results"] == []
            assert kwargs["x_values"] is None

def test_plot_multiple_curves_complex(old_style_collection):
    plotter = LoadDisplacementPlotter(old_style_collection)
    orig_getitem = ColumnCollection.__getitem__
    
    curves = [
        {"x": np.array([1]), "y": np.array([2])},
        {"type": "original"}, # will fallback to empty because no load_column
        {"type": "skeleton"},
        {"type": "cumulative"},
        {"type": "unknown"}
    ]
    with patch.object(ColumnCollection, "__getitem__", new=getitem_side_effect(orig_getitem)):
        with patch("tascpy.visualization.plotters.load_displacement.plotter.ld_plot.plot_multiple_curves") as mock_plot:
            plotter.plot_multiple_curves(curves)
            kwargs = mock_plot.call_args[1]
            curves_data = kwargs["curves_data"]
            # raw xy length = 1
            # unknown skipped
            # original, skeleton, cumulative -> total 4
            assert len(curves_data) == 4
