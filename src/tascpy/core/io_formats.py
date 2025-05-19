"""
ファイル入出力フォーマットの定義モジュール

このモジュールでは、ファイル入出力時のフォーマット設定を定義します。
各フォーマットは辞書として定義され、FILE_FORMATSに登録されます。
"""

from typing import Dict, Any

# 標準フォーマット定義
STANDARD_FORMAT = {
    "delimiter": "\t",
    "title_row": 0,
    "ch_row": 1,
    "name_row": 2,
    "unit_row": 3,
    "data_start_row": 4,
    "step_col": 0,
    "date_col": 1,
    "time_col": 2,
    "data_start_col": 3,
    "encoding": "utf-8",  # 標準フォーマットはUTF-8
    "use_channel_name": False,  # 列名（name）ベースで保存
}

# CSVフォーマット定義
CSV_FORMAT = {
    "delimiter": ",",
    "title_row": 0,
    "ch_row": 1,
    "name_row": 2,
    "unit_row": 3,
    "data_start_row": 4,
    "step_col": 0,
    "date_col": 1,
    "time_col": 2,
    "data_start_col": 3,
    "encoding": "utf-8",  # CSVフォーマットもUTF-8
    "use_channel_name": False,  # 列名（name）ベースで保存
}

# TASCフォーマット定義 (以前のW-Nフォーマット)
TASC_TXT_FORMAT = {
    "delimiter": "\t",
    "title_row": 0,
    "ch_row": 1,  # 2行目にチャンネル名がある
    "name_row": 2,  # チャンネル名をそのまま列名として使用
    "unit_row": 3,  # 3行目に単位がある
    "data_start_row": 4,  # 4行目からデータが始まる
    "step_col": 0,  # ﾃﾞｰﾀ番号
    "date_col": 1,  # 日付
    "time_col": 2,  # 時刻
    "data_start_col": 3,  # CH0 から始まる
    "encoding": "shift_jis",  # TASCフォーマットはShift-JIS
    "use_channel_name": True,  # チャンネル名（ch）ベースで保存
}

# TASCフォーマット定義 (以前のW-Nフォーマット)
TASC_CSV_FORMAT = {
    "delimiter": ",",
    "title_row": 0,
    "ch_row": 1,  # 2行目にチャンネル名がある
    "name_row": 2,  # チャンネル名をそのまま列名として使用
    "unit_row": 3,  # 3行目に単位がある
    "data_start_row": 4,  # 4行目からデータが始まる
    "step_col": 0,  # ﾃﾞｰﾀ番号
    "date_col": 1,  # 日付
    "time_col": 2,  # 時刻
    "data_start_col": 3,  # CH0 から始まる
    "encoding": "shift_jis",  # TASCフォーマットはShift-JIS
    "use_channel_name": True,  # チャンネル名（ch）ベースで保存
}

# ファイルフォーマットのレジストリ
FILE_FORMATS: Dict[str, Dict[str, Any]] = {
    "standard": STANDARD_FORMAT,
    "csv": CSV_FORMAT,
    "tasc_txt": TASC_TXT_FORMAT,
    "tasc_csv": TASC_CSV_FORMAT,
}


def register_format(name: str, format_config: Dict[str, Any]) -> None:
    """新しいファイルフォーマットを登録する

    Args:
        name: フォーマット名
        format_config: フォーマット設定の辞書
    """
    FILE_FORMATS[name] = format_config


def get_format(name: str) -> Dict[str, Any]:
    """指定された名前のファイルフォーマット設定を取得する

    Args:
        name: フォーマット名

    Returns:
        Dict[str, Any]: フォーマット設定

    Raises:
        KeyError: 指定された名前のフォーマットが存在しない場合
    """
    if name not in FILE_FORMATS:
        raise KeyError(f"ファイルフォーマット '{name}' は登録されていません")
    return FILE_FORMATS[name]
