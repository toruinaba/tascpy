"""Visualization module for tascpy"""
from .config import configure_plotting
from .core.plotter import CorePlotter
from ..core.collection import ColumnCollection

ColumnCollection.register_accessor("plot", CorePlotter)
