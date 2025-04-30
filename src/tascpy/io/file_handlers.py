"""
ファイル入出力のための補助モジュール

各種ファイル形式の読み込みと書き込みを担当するユーティリティ関数群
"""

from pathlib import Path
from typing import Union
from ..core.collection import ColumnCollection


def load_from_file(file_path: Union[str, Path], format_name: str = "tasc", **kwargs):
    """ファイルからデータを読み込む

    Args:
        file_path: 読み込むファイルのパス
        format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc"）
        **kwargs: フォーマット設定を上書きするためのキーワード引数

    Returns:
        ColumnCollection: 読み込んだデータを含むColumnCollectionオブジェクト
    """
    return ColumnCollection.from_file(file_path, format_name, **kwargs)


def save_to_file(
    collection: ColumnCollection,
    file_path: Union[str, Path],
    format_name: str = "tasc",
    **kwargs
):
    """データをファイルに保存する

    Args:
        collection: 保存するColumnCollectionオブジェクト
        file_path: 保存先ファイルパス
        format_name: 使用するファイルフォーマットの名前（デフォルト: "tasc"）
        **kwargs: フォーマット設定を上書きするためのキーワード引数
    """
    collection.to_file(file_path, format_name, **kwargs)


def load_tasc_file(file_path: Union[str, Path], **kwargs):
    """TASCファイルからデータを読み込む

    Args:
        file_path: 読み込むTASCファイルのパス
        **kwargs: 追加のフォーマット設定オプション

    Returns:
        ColumnCollection: 読み込んだTASCデータを含むColumnCollectionオブジェクト
    """
    return load_from_file(file_path, format_name="tasc", **kwargs)
