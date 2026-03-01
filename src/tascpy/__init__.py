"""
tascpy - 実験データ処理のためのPythonライブラリ
"""

import warnings

__version__ = "0.1.0"
__all__ = ["ColumnCollection", "Column", "Experiment", "CollectionOperations"]

# Visualization configuration
try:
    from .visualization.config import configure_plotting
    configure_plotting()
except ImportError:
    pass # visualization module might not be fully available during some imports

# 公開APIのインポート
from .experiment import Experiment
from .io.file_handlers import load_from_file, save_to_file
from .core import ColumnCollection, Column
from .analytics.operations.proxy import CollectionOperations
