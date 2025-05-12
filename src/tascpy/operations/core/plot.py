"""プロットに関する操作モジュール"""

from typing import Optional, Union, List, Dict, Any
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
    """グラフを描画します

    コレクション内のデータを散布図または線グラフとして可視化します。
    x軸またはy軸にstepを使用することもできます。

    Args:
        collection: 対象コレクション
        x_column: x軸の列名（None の場合は step を使用）
        y_column: y軸の列名（None の場合は step を使用）
        plot_type: プロットの種類（'scatter' または 'line'）
        ax: 既存の Axes オブジェクト（None の場合は新しい図を作成）
        **kwargs: Matplotlib のプロット関数に渡す追加のキーワード引数

    Returns:
        ColumnCollection: 元のコレクション

    Examples:
        >>> # 散布図の描画
        >>> collection.plot('x_col', 'y_col')
        >>>
        >>> # step を x軸として使用
        >>> collection.plot(None, 'y_col')
        >>>
        >>> # step を y軸として使用
        >>> collection.plot('x_col', None)
        >>>
        >>> # 線グラフの描画
        >>> collection.plot('x_col', 'y_col', plot_type='line', color='red')
        >>>
        >>> # 既存の axes に追加
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

    # グラフを表示
    plt.show()

    # 元のコレクションを返す
    return collection


@operation(domain="core")
def visualize_outliers(
    collection: ColumnCollection,
    column: str,
    window_size: int = 3,
    threshold: float = 0.5,
    x_column: Optional[str] = None,
    highlight_color: str = "red",
    plot_type: str = "scatter",
    show_normal: bool = True,
    normal_color: str = "blue",
    normal_alpha: float = 0.6,
    outlier_marker: str = "o",
    outlier_size: int = 80,
    ax: Optional[plt.Axes] = None,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
    **kwargs,
) -> ColumnCollection:
    """異常値を可視化します

    指定された列の異常値を検出し、視覚的に強調表示します。
    元のデータをプロットし、その上に異常値のみマーカーで強調表示します。
    detect_outliers 関数を内部で使用して異常値を特定します。

    Args:
        collection: 対象コレクション
        column: 異常値を検出する列の名前
        window_size: 移動平均のウィンドウサイズ（奇数推奨）
        threshold: 異常値とみなす移動平均との差分比率の閾値
        x_column: x軸の列名（None の場合は step を使用）
        highlight_color: 異常値のマーカー色
        plot_type: 通常データのプロットタイプ（'scatter' または 'line'）
        show_normal: 通常のデータポイントも表示するかどうか
        normal_color: 通常のデータポイントの色
        normal_alpha: 通常のデータポイントの透明度
        outlier_marker: 異常値のマーカースタイル
        outlier_size: 異常値のマーカーサイズ
        ax: 既存の Axes オブジェクト（None の場合は新しい図を作成）
        edge_handling: エッジ処理方法（"symmetric", "asymmetric"）
        min_abs_value: 比率計算時の最小絶対値
        scale_factor: スケール調整係数
        **kwargs: プロット関数に渡す追加のキーワード引数

    Returns:
        ColumnCollection: 異常値検出フラグを含む新しいコレクション

    Examples:
        >>> # 基本的な異常値の可視化
        >>> collection.ops.visualize_outliers('pressure_data').end()
        >>>
        >>> # 異常値検出パラメータのカスタマイズ
        >>> collection.ops.visualize_outliers(
        ...     'temperature',
        ...     window_size=5,
        ...     threshold=0.3
        ... ).end()
        >>>
        >>> # 表示スタイルのカスタマイズ
        >>> collection.ops.visualize_outliers(
        ...     'sensor_value',
        ...     highlight_color='magenta',
        ...     outlier_marker='x',
        ...     outlier_size=100,
        ...     show_normal=False
        ... ).end()
        >>>
        >>> # 複数の可視化を一つの図に表示
        >>> fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        >>> collection.ops.visualize_outliers(
        ...     'pressure', window_size=5, ax=ax1
        ... ).end()
        >>> collection.ops.visualize_outliers(
        ...     'temperature', threshold=0.3, ax=ax2
        ... ).end()
        >>> plt.tight_layout()
        >>> plt.show()
    """
    from ..core.stats import detect_outliers

    # 指定された列が存在するか確認
    if column not in collection.columns:
        raise KeyError(f"列 '{column}' は存在しません")

    # 異常値検出の実行
    outlier_column = f"_outlier_flags_{column}"
    result = detect_outliers(
        collection,
        column=column,
        window_size=window_size,
        threshold=threshold,
        result_column=outlier_column,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )

    # x軸データの取得
    if x_column is None:
        # stepをx軸として使用
        x_values = result.step.values
        x_name = "Step"
        x_unit = ""
    else:
        # 指定された列が存在するか確認
        if x_column not in result.columns:
            raise KeyError(f"列 '{x_column}' は存在しません")
        # 指定された列を使用
        x_col = result.columns[x_column]
        x_values = x_col.values
        x_name = x_col.name
        x_unit = x_col.unit

    # y軸（対象列）のデータを取得
    y_col = result.columns[column]
    y_values = y_col.values
    y_name = y_col.name
    y_unit = y_col.unit

    # 異常値フラグに基づいてデータポイントを分離
    outlier_indices = [
        i for i, flag in enumerate(result[outlier_column].values) if flag == 1
    ]
    normal_indices = [
        i for i, flag in enumerate(result[outlier_column].values) if flag == 0
    ]

    outlier_x = [x_values[i] for i in outlier_indices]
    outlier_y = [y_values[i] for i in outlier_indices]

    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # 軸ラベルの設定
    x_label = f"{x_name} [{x_unit}]" if x_unit else x_name
    y_label = f"{y_name} [{y_unit}]" if y_unit else y_name

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(f"異常値検出: {y_name}")

    # 重要な変更: すべてのデータをまずプロット（線または散布図）
    if show_normal:
        if plot_type == "scatter":
            ax.scatter(
                x_values,
                y_values,
                color=normal_color,
                alpha=normal_alpha,
                label="通常データ",
                **kwargs,
            )
        elif plot_type == "line":
            ax.plot(
                x_values,
                y_values,
                color=normal_color,
                alpha=normal_alpha,
                label="通常データ",
                **kwargs,
            )
        else:
            raise ValueError(
                "plot_type は 'scatter' または 'line' のいずれかである必要があります"
            )

    # 異常値のみを強調表示（元のデータポイント上に）
    if outlier_indices:
        print(f"visualize_outliers: {len(outlier_indices)}個の異常値をプロットします")
        print(
            f"最初の3つの異常値データ: {list(zip(outlier_x[:3], outlier_y[:3])) if outlier_x else '空'}"
        )

        ax.scatter(
            outlier_x,
            outlier_y,
            color=highlight_color,
            s=outlier_size,
            marker=outlier_marker,
            label="異常値",
            zorder=10,  # 他のデータポイントより前面に表示
        )
    else:
        print("visualize_outliers: 異常値がありません")

    # 異常値の数をタイトルに表示（オプション）
    outlier_count = len(outlier_indices)
    ax.set_title(f"異常値検出: {y_name} (検出数: {outlier_count}個)")

    # 凡例を表示
    if (show_normal and len(x_values) > 0) or outlier_indices:
        ax.legend()

    # グリッド線を追加して読みやすくする
    ax.grid(True, alpha=0.3)

    # 注: plt.show()をコメントアウト - これはインタラクティブ環境で必要ですが
    # スクリプト内で複数回呼び出すと問題を引き起こす可能性があります
    # plt.tight_layout() は呼び出し元で実行します

    # 異常値検出結果を含むコレクションを返す
    return result
