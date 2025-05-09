"""プロットに関する操作モジュール"""

from typing import Optional
import matplotlib.pyplot as plt
import matplotlib as mpl

# 日本語フォントサポート
try:
    import japanize_matplotlib

    # マイナス記号を正しく表示するための設定
    mpl.rcParams["axes.unicode_minus"] = False
except ImportError:
    print(
        "警告: japanize_matplotlib をインポートできません。日本語が正しく表示されない可能性があります。"
    )

from ...core.collection import ColumnCollection
from ...operations.registry import operation


@operation(domain="core")
def plot(
    collection: ColumnCollection,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    plot_type: str = "scatter",
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> ColumnCollection:
    """グラフを描画する

    Args:
        collection: 対象コレクション
        x_column: x軸の列名（Noneの場合はstepを使用）
        y_column: y軸の列名（Noneの場合はstepを使用）
        plot_type: プロットの種類 ('scatter' または 'line')
        ax: 既存のAxesオブジェクト（Noneの場合は新しい図を作成）
        **kwargs: Matplotlibのプロット関数に渡す追加のキーワード引数

    Returns:
        ColumnCollection: 元のコレクション

    Examples:
        >>> # 散布図の描画
        >>> collection.plot('x_col', 'y_col')
        >>>
        >>> # stepをx軸として使用
        >>> collection.plot(None, 'y_col')
        >>>
        >>> # stepをy軸として使用
        >>> collection.plot('x_col', None)
        >>>
        >>> # 線グラフの描画
        >>> collection.plot('x_col', 'y_col', plot_type='line', color='red')
        >>>
        >>> # 既存のaxesに追加
        >>> fig, ax = plt.subplots()
        >>> collection.plot('x_col', 'y_col', ax=ax)
        >>> collection.plot('x_col2', 'y_col2', ax=ax)  # 2つ目のプロットを追加
    """
    # x軸とy軸のデータを取得
    if x_column is None:
        # stepをx軸として使用
        x_values = collection.step.values
        x_name = "Step"
        x_unit = ""
    else:
        # 指定された列が存在するか確認
        if x_column not in collection.columns:
            raise KeyError(f"列 '{x_column}' は存在しません")
        # 指定された列を使用
        x_col = collection.columns[x_column]
        x_values = x_col.values
        x_name = x_col.name
        x_unit = x_col.unit

    if y_column is None:
        # stepをy軸として使用
        y_values = collection.step.values
        y_name = "Step"
        y_unit = ""
    else:
        # 指定された列が存在するか確認
        if y_column not in collection.columns:
            raise KeyError(f"列 '{y_column}' は存在しません")
        # 指定された列を使用
        y_col = collection.columns[y_column]
        y_values = y_col.values
        y_name = y_col.name
        y_unit = y_col.unit

    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig, ax = plt.subplots()

    # プロットの種類に応じて描画
    if plot_type == "scatter":
        ax.scatter(x_values, y_values, **kwargs)
    elif plot_type == "line":
        ax.plot(x_values, y_values, **kwargs)
    else:
        raise ValueError(
            "plot_type は 'scatter' または 'line' のいずれかである必要があります"
        )

    # 軸ラベルの設定（name [unit]の形式）
    x_label = f"{x_name} [{x_unit}]" if x_unit else x_name
    y_label = f"{y_name} [{y_unit}]" if y_unit else y_name

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(f"{plot_type.capitalize()} plot of {y_name} vs {x_name}")

    # plt.show()の呼び出しを削除（ユーザー側で必要に応じて呼び出す）

    # 元のコレクションを返す
    return collection
