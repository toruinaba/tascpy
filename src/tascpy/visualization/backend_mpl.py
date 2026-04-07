"""Matplotlib backend for tascpy visualization"""
from typing import Optional, Union, List, Dict, Any, Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

# Core plotting functions
def plot(
    x_values: Any,
    y_values: Any,
    x_label: str = "",
    y_label: str = "",
    title: str = "",
    plot_type: str = "line",
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    """基本プロット関数
    
    Args:
        x_values: X軸データ
        y_values: Y軸データ
    """
    created_new = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
        created_new = True
        
    if plot_type == "scatter":
        ax.scatter(x_values, y_values, **kwargs)
    elif plot_type == "line":
        ax.plot(x_values, y_values, **kwargs)
    else:
        # Default to plot
        ax.plot(x_values, y_values, **kwargs)
        
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)
        
    if created_new:
        plt.show()
        
    return ax

def plot_multiple(
    data_list: List[Dict[str, Any]],
    ax: Optional[Axes] = None,
    title: str = "",
    legend: bool = True
) -> Axes:
    """複数データのプロット"""
    created_new = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
        created_new = True
        
    for data in data_list:
        x = data.get("x")
        y = data.get("y")
        kwargs = data.get("kwargs", {})
        plot_type = data.get("type", "line")
        
        if plot_type == "scatter":
            ax.scatter(x, y, **kwargs)
        else:
            ax.plot(x, y, **kwargs)
            
    if title:
        ax.set_title(title)
    if legend:
        ax.legend()
        
    ax.grid(True, linestyle="--", alpha=0.7)
    
    if created_new:
        plt.show()
        
    return ax

# Advanced plotting (Load-Displacement specific logic can be generalized or kept here)
# Since we want to remove domain-specific logic from backend as much as possible,
# we should keep the backend generic. Domain-specific plot functions should prepare data
# and then call backend functions.

# BUT, for now, to replicate existing features quickly:

def create_figure(figsize: Tuple[float, float] = (8, 6)) -> Axes:
    """Create a new figure and return its axes"""
    fig, ax = plt.subplots(figsize=figsize)
    return ax

def scatter_points(
    x: List[float], 
    y: List[float], 
    ax: Optional[Axes] = None, 
    **kwargs
) -> Axes:
    """Scatter plot wrapper"""
    created_new = False
    if ax is None:
        ax = create_figure()
        created_new = True
        
    ax.scatter(x, y, **kwargs)
    
    if created_new:
        plt.show()
        
    return ax

def draw_line(
    x: List[float],
    y: List[float],
    ax: Axes,
    **kwargs
) -> Any:
    return ax.plot(x, y, **kwargs)

def draw_axline(
    ax: Axes,
    xy1: Tuple[float, float],
    slope: float,
    **kwargs
) -> Any:
    return ax.axline(xy1=xy1, slope=slope, **kwargs)

def draw_arrow(
    ax: Axes,
    x: float, y: float, dx: float, dy: float,
    **kwargs
) -> Any:
    return ax.arrow(x, y, dx, dy, **kwargs)

def add_text(
    ax: Axes,
    x: float,
    y: float,
    text: str,
    **kwargs
) -> Any:
    return ax.text(x, y, text, **kwargs)

def add_legend(ax: Axes, **kwargs) -> None:
    ax.legend(**kwargs)

def add_grid(ax: Axes, linestyle="--", alpha=0.7, **kwargs) -> None:
    ax.grid(True, linestyle=linestyle, alpha=alpha, **kwargs)

def set_labels(
    ax: Axes,
    xlabel: str = "",
    ylabel: str = "",
    title: str = ""
) -> None:
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    if title: ax.set_title(title)

def show_plot() -> None:
    plt.show()
