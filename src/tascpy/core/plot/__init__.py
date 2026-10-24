"""tascpy.core.plot - 汎用の描画（`coll.plot`）

このパッケージを初めて import したときに日本語フォントを登録します（`import tascpy` だけでは matplotlib を読み込みません）。
"""

from .font import enable_japanese_font

enable_japanese_font()

from .plotter import CorePlotter, axis_label  # noqa: E402

__all__ = ["CorePlotter", "axis_label", "enable_japanese_font"]
