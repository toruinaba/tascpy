import pytest
from unittest.mock import MagicMock, patch

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from tascpy.visualization import backend_plotly as bp

pytestmark = pytest.mark.skipif(not HAS_PLOTLY, reason="Plotly is not installed")

def test_check_plotly_availability():
    # If HAS_PLOTLY is True, this should not raise
    bp.check_plotly_availability()
    
    # Force it to False to test the error
    original_state = bp.HAS_PLOTLY
    bp.HAS_PLOTLY = False
    with pytest.raises(ImportError, match="Plotly is required for interactive plotting"):
        bp.check_plotly_availability()
    bp.HAS_PLOTLY = original_state

def test_plot_basic():
    fig = bp.plot([1, 2], [3, 4], x_label="X", y_label="Y", title="Title")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert list(fig.data[0].x) == [1, 2]
    assert list(fig.data[0].y) == [3, 4]
    
    # Check layout
    layout = fig.layout
    assert layout.title.text == "Title"
    assert layout.xaxis.title.text == "X"
    assert layout.yaxis.title.text == "Y"

def test_plot_scatter_with_kwargs():
    fig = bp.plot(
        [1, 2], [3, 4], 
        plot_type="scatter", 
        color="red", 
        name="MyScatter"
    )
    assert len(fig.data) == 1
    trace = fig.data[0]
    assert trace.mode == "markers"
    assert trace.marker.color == "red"
    assert trace.name == "MyScatter"

def test_plot_line_with_kwargs():
    fig = bp.plot(
        [1, 2], [3, 4], 
        plot_type="line", 
        color="blue", 
        name="MyLine"
    )
    assert len(fig.data) == 1
    trace = fig.data[0]
    assert trace.mode == "lines"
    assert trace.line.color == "blue"
    assert trace.name == "MyLine"

def test_plot_with_existing_fig():
    fig = go.Figure()
    res = bp.plot([1, 2], [3, 4], fig=fig, name="Added")
    assert res is fig
    assert len(fig.data) == 1

def test_create_figure():
    fig = bp.create_figure()
    assert isinstance(fig, go.Figure)

def test_scatter_points():
    fig = bp.scatter_points([1, 2], [3, 4], name="SP")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].mode == "markers"
    assert fig.data[0].name == "SP"

def test_draw_line():
    fig = bp.draw_line([1, 2], [3, 4], name="DL")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].mode == "lines"
    assert fig.data[0].name == "DL"

def test_add_annotation():
    fig = go.Figure()
    bp.add_annotation(fig, 1.0, 2.0, "TestAnno", showarrow=True)
    assert len(fig.layout.annotations) == 1
    ann = fig.layout.annotations[0]
    assert ann.text == "TestAnno"
    assert ann.x == 1.0
    assert ann.y == 2.0
    assert ann.showarrow is True

def test_draw_arrow():
    fig = go.Figure()
    bp.draw_arrow(fig, 1.0, 2.0, 0.5, 0.5, ec="blue")
    assert len(fig.layout.annotations) == 1
    arr = fig.layout.annotations[0]
    # tail is 1.0, 2.0. head is 1.5, 2.5
    assert arr.x == 1.5
    assert arr.y == 2.5
    assert arr.ax == 1.0
    assert arr.ay == 2.0
    assert arr.arrowcolor == "blue"
    assert arr.showarrow is True

    # test fc
    fig2 = go.Figure()
    bp.draw_arrow(fig2, 1.0, 2.0, 0.5, 0.5, fc="green")
    assert fig2.layout.annotations[0].arrowcolor == "green"

def test_set_labels():
    fig = go.Figure()
    bp.set_labels(fig, xlabel="XLabel", ylabel="YLabel", title="My Title")
    assert fig.layout.xaxis.title.text == "XLabel"
    assert fig.layout.yaxis.title.text == "YLabel"
    assert fig.layout.title.text == "My Title"

def test_show_plot():
    fig = MagicMock()
    bp.show_plot(fig)
    fig.show.assert_called_once()
