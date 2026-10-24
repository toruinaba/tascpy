"""日本語フォントの登録

`tascpy.core.plot` を初めて import したとき（`coll.plot` の初回アクセスなど）に、japanize-matplotlib に同梱の IPAex ゴシックを matplotlib に登録して既定のフォントにします。
変更するのは日本語の表示に必要な font.family と axes.unicode_minus（IPAex にはマイナス記号 U+2212 がない）だけです。
japanize_matplotlib モジュール自体は import しません（Python 3.12 で削除された distutils に依存しているため）。
"""

import importlib.util
import warnings
from pathlib import Path
from typing import Optional

import matplotlib as mpl
from matplotlib import font_manager

JAPANESE_FONT = "IPAexGothic"


def _bundled_font_path() -> Optional[Path]:
    spec = importlib.util.find_spec("japanize_matplotlib")
    if spec is None or spec.origin is None:
        return None
    path = Path(spec.origin).parent / "fonts" / "ipaexg.ttf"
    return path if path.exists() else None


def enable_japanese_font() -> bool:
    """日本語フォント（IPAex ゴシック）を登録して既定のフォントにする

    Returns:
        bool: フォントを登録できたかどうか（japanize-matplotlib が見つからなければ False）
    """
    path = _bundled_font_path()
    if path is None:
        warnings.warn("japanize-matplotlib が見つからないため、日本語が正しく表示されない可能性があります", stacklevel=2)
        return False
    font_manager.fontManager.addfont(str(path))
    mpl.rcParams["font.family"] = JAPANESE_FONT
    mpl.rcParams["axes.unicode_minus"] = False
    return True
