import pytest
from unittest.mock import patch, MagicMock
from tascpy.visualization import backend_mpl as bm
import matplotlib.pyplot as plt

def test_plot_multiple_new_ax():
    # If ax is None, it creates a new fig, ax, plots them all, then returns ax
    data = [
        {"x": [1, 2], "y": [3, 4], "type": "line", "kwargs": {"color": "red"}},
        {"x": [1, 2], "y": [4, 5], "type": "scatter"}
    ]
    with patch("matplotlib.pyplot.show") as mock_show:
        ax = bm.plot_multiple(data, ax=None, title="Test", legend=True)
        assert mock_show.called
        assert ax is not None
        assert ax.get_title() == "Test"
        # 1 line, 1 PathCollection (scatter)
        assert len(ax.lines) == 1
        assert len(ax.collections) == 1

def test_plot_multiple_existing_ax():
    fig, ax = plt.subplots()
    data = [
        {"x": [1, 2], "y": [3, 4], "type": "line"}
    ]
    with patch("matplotlib.pyplot.show") as mock_show:
        res = bm.plot_multiple(data, ax=ax, title="Existing")
        assert not mock_show.called
        assert res is ax
        assert ax.get_title() == "Existing"

def test_plot_new_ax_line():
    with patch("matplotlib.pyplot.show") as mock_show:
        ax = bm.plot([1, 2], [3, 4], plot_type="line", x_label="x", y_label="y", title="hi")
        assert mock_show.called
        assert len(ax.lines) == 1
        assert ax.get_xlabel() == "x"
        assert ax.get_ylabel() == "y"
        assert ax.get_title() == "hi"

def test_plot_new_ax_scatter():
    with patch("matplotlib.pyplot.show") as mock_show:
        ax = bm.plot([1, 2], [3, 4], plot_type="scatter")
        assert mock_show.called
        assert len(ax.collections) == 1

def test_plot_new_ax_default():
    with patch("matplotlib.pyplot.show") as mock_show:
        ax = bm.plot([1, 2], [3, 4], plot_type="unknown")
        assert mock_show.called
        assert len(ax.lines) == 1

def test_scatter_points_new_ax():
    with patch("matplotlib.pyplot.show") as mock_show:
        ax = bm.scatter_points([1, 2], [3, 4])
        assert mock_show.called
        assert len(ax.collections) == 1
