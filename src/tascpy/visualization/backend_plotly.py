"""Plotly backend for tascpy visualization"""
import importlib.util
from typing import Any, List, Optional

HAS_PLOTLY = importlib.util.find_spec("plotly") is not None


def check_plotly_availability() -> None:
    if not HAS_PLOTLY:
        raise ImportError("Plotly is required for interactive plotting. Please install it with `pip install plotly`.")


def _graph_objects() -> Any:
    check_plotly_availability()
    import plotly.graph_objects as go

    return go

def plot(
    x_values: Any,
    y_values: Any,
    x_label: str = "",
    y_label: str = "",
    title: str = "",
    plot_type: str = "line",
    fig: Any = None,
    name: str = "Data",
    **kwargs
) -> Any:
    """Plotly で折れ線（plot_type="line"）または散布図（"scatter"）を描画します

    color は線・マーカーの色として扱い、それ以外の kwargs は go.Scatter にそのまま渡します。
    title / x_label / y_label は指定されていれば既存の Figure にも設定します。
    """
    go = _graph_objects()
    if fig is None:
        fig = go.Figure()
        fig.update_layout(template="plotly_white")

    color = kwargs.pop("color", None)
    style_key = "marker" if plot_type == "scatter" else "line"
    style = dict(kwargs.pop(style_key, {}) or {})
    if color is not None:
        style.setdefault("color", color)
    fig.add_trace(go.Scatter(
        x=x_values, y=y_values, mode="markers" if plot_type == "scatter" else "lines", name=name,
        **{style_key: style}, **kwargs,
    ))
    set_labels(fig, xlabel=x_label, ylabel=y_label, title=title)
    return fig


def create_figure() -> Any:
    """Create a new plotly figure"""
    return _graph_objects().Figure()

def scatter_points(
    x: List[float], 
    y: List[float], 
    fig: Any = None,
    name: str = "Data",
    **kwargs
) -> Any:
    """Scatter plot wrapper"""
    return plot(x, y, plot_type="scatter", fig=fig, name=name, **kwargs)

def draw_line(
    x: List[float],
    y: List[float],
    fig: Any = None,
    name: str = "Line",
    **kwargs
) -> Any:
    return plot(x, y, plot_type="line", fig=fig, name=name, **kwargs)

def add_annotation(
    fig: Any,
    x: float,
    y: float,
    text: str,
    showarrow: bool = False,
    **kwargs
) -> Any:
    """Add annotation (text) to figure"""
    fig.add_annotation(x=x, y=y, text=text, showarrow=showarrow, **kwargs)
    return fig

def draw_arrow(
    fig: Any,
    x: float, y: float, dx: float, dy: float,
    **kwargs
) -> Any:
    """Draw an arrow using annotation"""
    # Plotly uses ax, ay (offsets/coordinates) for arrows in annotations
    # Here we simulate vector arrow from (x,y) to (x+dx, y+dy)
    
    # arrow properties
    arrowcolor = kwargs.get('ec', 'black') # map mpl edge color
    if 'fc' in kwargs: arrowcolor = kwargs['fc']
    
    # annotation with arrow
    fig.add_annotation(
        x=x+dx, y=y+dy, # head
        ax=x, ay=y,     # tail (ref='x', 'y' means these are coordinates, but plotly annotations use offsets by default unless axref/ayref set)
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor=arrowcolor
    )
    return fig

def set_labels(
    fig: Any,
    xlabel: str = "",
    ylabel: str = "",
    title: str = ""
) -> None:
    update_dict = {}
    if xlabel: update_dict['xaxis_title'] = xlabel
    if ylabel: update_dict['yaxis_title'] = ylabel
    if title: update_dict['title'] = title
    
    if update_dict:
        fig.update_layout(**update_dict)

def show_plot(fig: Any) -> None:
    fig.show()
