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


def add_point(
    ax: Optional[plt.Axes], x_data: float, y_data: float, text: Optional[str] = None
) -> Optional[plt.Axes]:
    """最大値をプロットする関数"""
    ax.scatter([x_data], [y_data], marker="o", color="r")
    if text:
        ax.text(x_data, y_data, text, fontsize=8, color="red", ha="center", va="bottom")
    return ax


def add_vertical_line(
    ax: Optional[plt.Axes], x_data: float, text: Optional[str] = None
) -> Optional[plt.Axes]:
    """垂直線をプロットする関数"""
    ax.axvline(x=x_data, color="gray", linestyle="--")
    if text:
        ax.text(
            x_data,
            ax.get_ylim()[1],
            text,
            fontsize=8,
            color="gray",
            ha="center",
            va="bottom",
        )
    return ax


def add_horizontal_line(
    ax: Optional[plt.Axes], y_data: float, text: Optional[str] = None
) -> Optional[plt.Axes]:
    """水平線をプロットする関数"""
    ax.axhline(y=y_data, color="gray", linestyle="--")
    if text:
        ax.text(
            ax.get_xlim()[1],
            y_data,
            text,
            fontsize=8,
            color="gray",
            ha="right",
            va="center",
        )
    return ax


def add_origin_line(
    ax: Optional[plt.Axes], slope: float, text: Optional[str] = None
) -> Optional[plt.Axes]:
    """原点を通る直線をプロットする関数"""
    ax.axline((0, 0), slope=slope, color="gray", linestyle="--")
    if text:
        ax.text(
            ax.get_xlim()[1],
            slope * ax.get_xlim()[1],
            text,
            fontsize=8,
            color="gray",
            ha="right",
            va="center",
        )
    return ax


def add_line_with_slope(
    ax: Optional[plt.Axes],
    slope: float,
    point: tuple,
    text: Optional[str] = None,
) -> Optional[plt.Axes]:
    """指定した傾きと点を通る直線をプロットする関数"""
    ax.axline(point, slope=slope, color="gray", linestyle="--")
    if text:
        x_data, y_data = point
        ax.text(
            x_data,
            y_data,
            text,
            fontsize=8,
            color="gray",
            ha="right",
            va="center",
        )
    return ax


def add_x_max(
    ax: Optional[plt.Axes],
    x_data: List[float],
    y_data: List[float],
    text: Optional[str] = None,
) -> Optional[plt.Axes]:
    """最大値をプロットする関数"""
    max_index = y_data.index(max(y_data))
    x_max = x_data[max_index]
    y_max = y_data[max_index]
    if text is None:
        text = f"{x_max:.2f}"
    ax = add_point(ax, x_max, y_max, text)
    return ax


def add_x_min(
    ax: Optional[plt.Axes],
    x_data: List[float],
    y_data: List[float],
    text: Optional[str] = None,
) -> Optional[plt.Axes]:
    """最小値をプロットする関数"""
    min_index = y_data.index(min(y_data))
    x_min = x_data[min_index]
    y_min = y_data[min_index]
    if text is None:
        text = f"{x_min:.2f}"
    ax = add_point(ax, x_min, y_min, text)
    return ax


def add_y_max(
    ax: Optional[plt.Axes],
    x_data: List[float],
    y_data: List[float],
    text: Optional[str] = None,
) -> Optional[plt.Axes]:
    """最大値をプロットする関数"""
    max_index = x_data.index(max(x_data))
    x_max = x_data[max_index]
    y_max = y_data[max_index]
    if text is None:
        text = f"{y_max:.2f}"
    ax = add_point(ax, x_max, y_max, text)
    return ax


def add_y_min(
    ax: Optional[plt.Axes],
    x_data: List[float],
    y_data: List[float],
    text: Optional[str] = None,
) -> Optional[plt.Axes]:
    """最小値をプロットする関数"""
    min_index = x_data.index(min(x_data))
    x_min = x_data[min_index]
    y_min = y_data[min_index]
    if text is None:
        text = f"{y_min:.2f}"
    ax = add_point(ax, x_min, y_min, text)
    return ax


def set_axis(
    ax: plt.Axes, x_label: str, y_label: str, title: Optional[str] = None
) -> plt.Axes:
    """軸の設定を行う関数"""
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)
    return ax
