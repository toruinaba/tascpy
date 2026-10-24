"""
tascpy.core.io - ファイルの読み込み・保存
"""

from .file_io import load_collection as load
from .file_io import load_from_stream, save_collection as save
from .formats import register_format
from .parquet import load_parquet, save_parquet
from .proxy import CollectionIO

__all__ = ["load", "load_from_stream", "save", "load_parquet", "save_parquet", "register_format", "CollectionIO"]
