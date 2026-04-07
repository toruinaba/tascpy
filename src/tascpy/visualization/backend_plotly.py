"""Plotly backend for tascpy visualization"""
from typing import Optional, Union, List, Dict, Any, Tuple
import numpy as np

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def check_plotly_availability():
    if not HAS_PLOTLY:
        raise ImportError("Plotly is required for interactive plotting. Please install it with `pip install plotly`.")

def plot(
    x_values: Any,
    y_values: Any,
    x_label: str = "",
    y_label: str = "",
    title: str = "",
    plot_type: str = "line",
    fig: Optional[Any] = None,
    name: str = "Data",
    **kwargs
) -> Any:
    """基本プロット関数 for Plotly
    
    Args:
        x_values: X軸データ
        y_values: Y軸データ
    """
    check_plotly_availability()
    
    created_new = False
    if fig is None:
        fig = go.Figure()
        created_new = True
        
    # kwargs adjustment for plotly
    mode = "lines"
    if plot_type == "scatter":
        mode = "markers"
        
    # Convert matplotlib-style kwargs to plotly if possible, or just ignore specific ones
    # basic conversion:
    marker_props = {}
    line_props = {}
    
    if "color" in kwargs:
        color = kwargs.pop("color")
        marker_props["color"] = color
        line_props["color"] = color
        
    trace_kwargs = {
        "x": x_values,
        "y": y_values,
        "mode": mode,
        "name": name
    }
    
    if plot_type == "scatter":
        trace_kwargs["marker"] = marker_props
    else:
        trace_kwargs["line"] = line_props
        
    # Add other kwargs
    # This is a simplification; a robust implementation would map mpl kwargs to plotly
    
    fig.add_trace(go.Scatter(**trace_kwargs))
        
    if created_new:
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            template="plotly_white"
        )
        # fig.show() is usually called by the user or in a notebook environment
        
    return fig

def create_figure() -> Any:
    """Create a new plotly figure"""
    check_plotly_availability()
    return go.Figure()

def scatter_points(
    x: List[float], 
    y: List[float], 
    fig: Optional[Any] = None,
    name: str = "Data",
    **kwargs
) -> Any:
    """Scatter plot wrapper"""
    return plot(x, y, plot_type="scatter", fig=fig, name=name, **kwargs)

def draw_line(
    x: List[float],
    y: List[float],
    fig: Optional[Any] = None,
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
