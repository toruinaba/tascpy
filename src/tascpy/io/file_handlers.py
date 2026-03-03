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
        **kwargs: フォーマット設定を上書きするためのキーワード引数。
            以下のパラメータを指定可能です：
            - encoding (str): 文字エンコーディング（例: "utf-8", "shift_jis"）
            - delimiter (str): 区切り文字
            - ch_row (int): チャンネル名が記載されている行インデックス(0始まり)
            - name_row (int): カラム名が記載されている行インデックス(0始まり)
            - unit_row (int): 単位が記載されている行インデックス(0始まり)
            - data_start_row (int): データが開始する行インデックス(0始まり)
            - data_start_col (int): データが開始する列インデックス(0始まり)
            - step_col (int): Step（インデックス）として使用する列インデックス
            - selected_columns (list[str]): 読み込むカラム名のリスト（指定した列のみ読み込みます）

    Returns:
        ColumnCollection: 読み込んだデータを含むColumnCollectionオブジェクト
    """
    import tascpy
    return tascpy.io.load(file_path, format_name=format_name, **kwargs)


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
    collection.io.save(file_path, format_name=format_name, **kwargs)


def load_tasc_file(file_path: Union[str, Path], **kwargs):
    """TASCファイルからデータを読み込む

    Args:
        file_path: 読み込むTASCファイルのパス
        **kwargs: 追加のフォーマット設定オプション。主なオプションは以下の通りです：
            - encoding (str): 文字エンコーディング（デフォルト: "utf-8" または "shift_jis"）
            - selected_columns (list[str]): 特定の列のみを読み込む場合はカラム名またはチャンネル名のリストを指定

    Returns:
        ColumnCollection: 読み込んだTASCデータを含むColumnCollectionオブジェクト
    """
    import tascpy
    return tascpy.io.load(file_path, format_name="tasc", **kwargs)
