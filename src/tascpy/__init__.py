"""
tascpy - 実験データ処理のためのPythonライブラリ
"""

import warnings

__version__ = "0.1.0"
__all__ = ["ColumnCollection", "Column"]

# 日本語フォントの自動設定を先に試行
japanize_available = False
try:
    import japanize_matplotlib
    import matplotlib as mpl

    # 警告抑制機能をコメントアウトして、実際の警告が表示されるか確認
    # warnings.filterwarnings("ignore", message="Glyph .* missing from font.*")
    # warnings.filterwarnings(
    #     "ignore", category=UserWarning, message=".*FigureCanvasAgg is non-interactive.*"
    # )

    mpl.rcParams["axes.unicode_minus"] = False  # マイナス記号を正しく表示
    japanize_available = True
except ImportError as e:
    # インポートエラーの詳細を警告として表示
    warnings.warn(
        f"japanize_matplotlib をインポートできませんでした: {e}。日本語が正しく表示されない可能性があります。"
        "setuptools パッケージをインストールすることで解決できる場合があります: pip install setuptools"
    )

# 公開APIのインポート
from .experiment import Experiment
from .io.file_handlers import load_from_file, save_to_file
from .core import ColumnCollection, Column
