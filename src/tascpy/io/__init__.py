"""
tascpy.io - ファイルの読み込み・保存
"""

from .file_io import load_collection as load
from .file_io import load_from_stream, save_collection as save
from .formats import register_format
from .proxy import CollectionIO

__all__ = ["load", "load_from_stream", "save", "register_format", "CollectionIO"]
