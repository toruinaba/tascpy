"""
tascpy.io - 入出力機能

このモジュールはファイルの読み込み・保存機能を提供します。
"""

from .file_handlers import load_from_file, save_to_file
from .file_io import load_collection as load, _load_from_stream as load_from_stream
from .proxy import CollectionIO
from tascpy.core.collection import ColumnCollection

ColumnCollection.register_accessor("io", CollectionIO)

__all__ = [
    "load",
    "load_from_stream",
    "load_from_file",
    "save_to_file",
]
