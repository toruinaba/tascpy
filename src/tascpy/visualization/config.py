from typing import Optional, Dict, Any
import matplotlib.pyplot as plt
import matplotlib as mpl

HAS_JAPANIZE_MATPLOTLIB = False
try:
    import japanize_matplotlib
    HAS_JAPANIZE_MATPLOTLIB = True
except ImportError:
    pass

def configure_plotting(use_japanese: bool = True, font_size: int = 11):
    """プロットの共通設定を行う

    Args:
        use_japanese: 日本語フォントを使用するかどうか
        font_size: フォントサイズ
    """
    # マイナス記号の表示設定
    mpl.rcParams["axes.unicode_minus"] = False
    
    # フォントサイズ
    plt.rcParams["font.size"] = font_size

    if use_japanese and HAS_JAPANIZE_MATPLOTLIB:
        # japanize_matplotlibはインポートするだけで適用される
        pass
    elif use_japanese and not HAS_JAPANIZE_MATPLOTLIB:
        print("Warning: japanize_matplotlib not found. Japanese text may not display correctly.")

# デフォルトで設定適用
configure_plotting()
