
import sys
import os
import pytest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step
import tascpy.operations.core.plot # Register operations


def create_collection():
    c = ColumnCollection(step=[], columns={})
    c.step = Step(values=[0.0, 1.0, 2.0, 3.0, 4.0])
    c.add_column("Val", NumberColumn(None, "Val", "m", values=[0, 10, 20, 30, 40]))
    c.add_column("Val2", NumberColumn(None, "Val2", "kg", values=[0, 1, 4, 9, 16]))
    return c

@pytest.fixture
def sample_collection():
    return create_collection()

def test_plot_basic(sample_collection):
    # Test fallback to step
    ax = sample_collection.ops.plot(y_column="Val")
    assert isinstance(ax, plt.Axes)
    assert ax.get_xlabel() == "Step"
    assert "Val [m]" in ax.get_ylabel()

def test_plot_xy(sample_collection):
    # Test X vs Y
    ax = sample_collection.ops.plot(x_column="Val", y_column="Val2")
    assert "Val [m]" in ax.get_xlabel()
    assert "Val2 [kg]" in ax.get_ylabel()

def test_plot_title_default(sample_collection):
    ax = sample_collection.ops.plot(y_column="Val")
    # Title format: "Scatter plot of Val vs Step"
    assert "Val vs Step" in ax.get_title()

def test_visualize_outliers(sample_collection):
    # Just verify it runs and returns collection
    res = sample_collection.ops.visualize_outliers(
        column="Val", 
        threshold=0.1, 
        show_normal=False
    ).end()
    assert isinstance(res, ColumnCollection)
    assert "_outlier_flags_Val" in res.columns

def test_plot_const_x(sample_collection):
    x = [0, 1]
    ax = sample_collection.ops.plot_const_x(
        x_values=x,
        y_columns=["Val", "Val2"]
    )
    assert isinstance(ax, plt.Axes)
    # Check lines (should be 1 line connecting the points)
    # backend_mpl.plot defaults to plot_type="line" which adds to ax.lines
    # If it was scatter, it would be ax.collections
    assert len(ax.lines) == 1 or len(ax.collections) == 1

if __name__ == "__main__":
    c = create_collection()
    test_plot_basic(c)
    test_plot_xy(c)
    test_plot_title_default(c)
    test_visualize_outliers(c)
    test_plot_const_x(c)
    print("All plot verification tests passed!")
