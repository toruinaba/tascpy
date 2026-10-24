"""
テキスト形式のファイルフォーマット定義

どのフォーマットも、ヘッダー（チャンネル行・名前行・単位行）の下にデータ行が続く TASC 系のレイアウトです。
読み込み時は行・列の位置を上書きできます。保存は常に標準レイアウト（下記の既定値）で書き出します。
"""

from typing import Any, Dict

_LAYOUT = {
    "ch_row": 1,
    "name_row": 2,
    "unit_row": 3,
    "data_start_row": 4,
    "step_col": 0,
    "date_col": 1,
    "time_col": 2,
    "data_start_col": 3,
}

FILE_FORMATS: Dict[str, Dict[str, Any]] = {
    "tasc_txt": {**_LAYOUT, "delimiter": "\t", "encoding": "shift_jis"},
    "tasc_csv": {**_LAYOUT, "delimiter": ",", "encoding": "shift_jis"},
    "standard": {**_LAYOUT, "delimiter": "\t", "encoding": "utf-8"},
    "csv": {**_LAYOUT, "delimiter": ",", "encoding": "utf-8"},
}
FILE_FORMATS["tasc"] = FILE_FORMATS["tasc_txt"]


def register_format(name: str, format_config: Dict[str, Any]) -> None:
    """フォーマットを登録する（指定しなかった項目は標準レイアウト・タブ区切り・UTF-8）"""
    FILE_FORMATS[name] = {**_LAYOUT, "delimiter": "\t", "encoding": "utf-8", **format_config}


def get_format(name: str) -> Dict[str, Any]:
    """フォーマット設定のコピーを返す

    Raises:
        KeyError: 登録されていないフォーマット名の場合
    """
    if name not in FILE_FORMATS:
        raise KeyError(f"ファイルフォーマット '{name}' は登録されていません")
    return dict(FILE_FORMATS[name])
