"""Visualization module for tascpy"""
from .config import configure_plotting
from .plotters.core.plotter import CorePlotter
from tascpy.core.collection import ColumnCollection

ColumnCollection.register_accessor("plot", CorePlotter)
