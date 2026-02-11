# Import matplotlib at module level for proper mocking in tests
from typing import Optional, Union, List
from matplotlib import pyplot as plt
import matplotlib as mpl


def configure_japanese_font():
    """日本語フォントの設定を行う関数

    japanize-matplotlibパッケージを使用して、
    プロット内の日本語テキストを正しく表示するための設定を適用します。
    """
    try:
        # japanize-matplotlibを使用した設定
        import japanize_matplotlib

        # テキストの乱れを防ぐためにテキストプロパティを設定
        mpl.rcParams["axes.unicode_minus"] = False

        # フォントサイズの設定
        plt.rcParams["font.size"] = 11
    except Exception as e:
        print(f"日本語フォント設定の適用に失敗しました: {e}")


# 日本語フォントの設定を適用
configure_japanese_font()


def plot_data(
    ax: Optional[plt.Axes],
    x_data: Union[List, float],
    y_data: Union[List, float],
    **kwargs: dict,
) -> Optional[plt.Axes]:
    """プロットする関数"""
    if not isinstance(x_data, list):
        x_data = [x_data]
    if not isinstance(y_data, list):
        y_data = [y_data]
    if ax:
        ax.plot(x_data, y_data, **kwargs)
    else:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x_data, y_data, **kwargs)
    return ax



    return ax
