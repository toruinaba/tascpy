"""プロットに関する操作モジュール"""

from typing import Optional, Union, List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np # Added numpy

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
from ..abstraction import inject_plot_data


@operation(domain="core")
@inject_plot_data(x_arg="x_column", y_arg="y_column")
def plot(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str,
    y_label: str,
    title: str,
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> plt.Axes:
    """グラフを描画します
    
    (backend_mpl.plot を使用)
    Args:
        x_values, y_values, x_label, y_label, title: @inject_plot_data により注入されます
    """
    from ...visualization import backend_mpl
    
    return backend_mpl.plot(
        x_values=x_values,
        y_values=y_values,
        x_label=x_label,
        y_label=y_label,
        title=title,
        ax=ax,
        **kwargs
    )


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
        >>> plt.show()  # 最後にまとめて表示
    """
    from ..core.stats import detect_outliers
    from ..core.filters import filter_by_value

    # 指定された列が存在するか確認


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

    # filter_by_valueを使用して正常値と異常値のデータを分離
    normal_data = filter_by_value(result, outlier_column, 0)
    outlier_data = filter_by_value(result, outlier_column, 1)
    outlier_count = len(outlier_data)

    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
        created_new_figure = True
    else:
        created_new_figure = False

    if show_normal:
        # 通常のデータをプロット - ここでaxを明示的に渡す
        plot_kwargs = kwargs.copy()
        plot_kwargs["color"] = normal_color
        plot_kwargs["alpha"] = normal_alpha
        plot_kwargs["plot_type"] = plot_type
        
        # plotは純粋関数になったのでデータを抽出して渡す
        if x_column is None:
            x_vals = result.step.values
            x_name = "Step"
            x_unit = ""
        else:
            x_vals = result[x_column].values
            x_name = result.columns[x_column].name
            x_unit = result.columns[x_column].unit
            
        y_vals = result[column].values
        y_name = result.columns[column].name
        y_unit = result.columns[column].unit
        
        x_lbl = f"{x_name} [{x_unit}]" if x_unit else x_name
        y_lbl = f"{y_name} [{y_unit}]" if y_unit else y_name
        title = f"{plot_type.capitalize()} plot of {y_name} vs {x_name}"

        plot(
            x_values=np.array(x_vals), 
            y_values=np.array(y_vals), 
            x_label=x_lbl, 
            y_label=y_lbl, 
            title=title, 
            ax=ax, 
            **plot_kwargs
        )

    # 異常値のプロット
    if outlier_count > 0:
        print(f"visualize_outliers: {outlier_count}個の異常値をプロットします")

        # 異常値データをプロット - 散布図として強調表示するためplot関数を使用
        outlier_kwargs = {
            "color": highlight_color,
            "plot_type": "scatter",  # 異常値は常に散布図で表示
            "s": outlier_size,
            "marker": outlier_marker,
            "label": "異常値",
            "zorder": 10,  # 他のデータポイントより前面に表示
        }

        # 先頭の3つの異常値データをデバッグ出力
        if x_column is None:
            outlier_x = outlier_data.step.values
        else:
            outlier_x = outlier_data[x_column].values

        outlier_y = outlier_data[column].values

        if len(outlier_x) > 0:
            # デバッグ情報を出力
            debug_count = min(3, len(outlier_x))
            print(
                f"最初の{debug_count}個の異常値データ: {list(zip(outlier_x[:debug_count], outlier_y[:debug_count]))}"
            )

        # 異常値データをプロット
        # 異常値データをプロット
        # outlier_data から値を抽出
        if x_column is None:
            out_x_vals = outlier_data.step.values
        else:
            out_x_vals = outlier_data[x_column].values
            
        out_y_vals = outlier_data[column].values
        
        # ラベル類は↑で計算したもの (normal plotting logic pass or not executed?)
        # If show_normal is False, we might not have calculated labels. 
        # Calculate labels if not done.
        if 'x_lbl' not in locals():
            if x_column is None:
                x_name = "Step"
                x_unit = ""
            else:
                x_name = getattr(collection.columns.get(x_column), "name", x_column)
                x_unit = getattr(collection.columns.get(x_column), "unit", "")
                
            y_name = getattr(collection.columns.get(column), "name", column)
            y_unit = getattr(collection.columns.get(column), "unit", "")
            
            x_lbl = f"{x_name} [{x_unit}]" if x_unit else x_name
            y_lbl = f"{y_name} [{y_unit}]" if y_unit else y_name
            title = f"Outlier detection of {y_name}"

        plot(
            x_values=np.array(out_x_vals), 
            y_values=np.array(out_y_vals), 
            x_label=x_lbl, 
            y_label=y_lbl, 
            title=title, 
            ax=ax, 
            **outlier_kwargs
        )
    else:
        print("visualize_outliers: 異常値がありません")

    # y軸の情報取得（タイトル表示用）
    y_col = result.columns[column]
    y_name = y_col.name

    # 異常値の数をタイトルに表示
    ax.set_title(f"異常値検出: {y_name} (検出数: {outlier_count}個)")

    # 凡例を表示（異常値があるか、正常値を表示している場合）
    if show_normal or outlier_count > 0:
        ax.legend()

    # グリッド線を追加して読みやすくする
    ax.grid(True, alpha=0.3)

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        plt.show()

    # 異常値検出結果を含むコレクションを返す

    return result


@operation(domain="core")
def plot_const_x(
    collection: ColumnCollection,
    x_values: List[float],
    y_columns: List[str],
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> plt.Axes:
    """指定されたX値（定数リスト）に対して、複数の列の値をYとしてプロットします
    注: 単一行のコレクションに対して使用することを想定しています
    
    Args:
        collection: ColumnCollection オブジェクト（通常は1行）
        x_values: X軸の値のリスト
        y_columns: Y軸として使用する列名のリスト
        ax: Axesオブジェクト
        **kwargs: plotの引数

    Returns:
        ColumnCollection: 元のコレクション
    """
    if len(x_values) != len(y_columns):
        raise ValueError(f"x_valuesの長さ({len(x_values)})とy_columnsの長さ({len(y_columns)})が一致しません")

    # 値を取得 (単一行を想定)
    y_vals_list = []
    
    # 欠損値を含む可能性があるため、すべてfloatとして扱い、NoneはNaNにする
    for col_name in y_columns:
        if col_name not in collection.columns:
             print(f"Warning: Column {col_name} not found")
             y_vals_list.append(float('nan'))
             continue
             
        col = collection.columns[col_name]
        vals = col.values
        if len(vals) > 0:
            val = vals[0]
            if val is None:
                y_vals_list.append(float('nan'))
            else:
                y_vals_list.append(float(val))
        else:
            y_vals_list.append(float('nan'))

    # NumPy配列に変換
    x_arr = np.array(x_values)
    y_arr = np.array(y_vals_list)
    
    # ラベル等の構築
    # plot_const_x は通常 titleなどをkwargsで受けるか、デフォルトを設定
    x_label = kwargs.pop("x_label", "X Parameters")
    y_label = kwargs.pop("y_label", "Y Values")
    title = kwargs.pop("title", f"Plot of {len(y_columns)} columns vs X")
    
    # 純粋関数 plot を呼び出し
    return plot(
        x_values=x_arr,
        y_values=y_arr,
        x_label=x_label,
        y_label=y_label,
        title=title,
        ax=ax,
        **kwargs
    )


@operation(domain="core")
@inject_plot_data(x_arg="x_column", y_arg="y_column")
def iplot(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str,
    y_label: str,
    title: str,
    fig: Optional[Any] = None,
    **kwargs,
) -> Any:
    """インタラクティブなグラフを描画します (Plotly使用)

    Args:
        x_values, y_values, x_label, y_label, title: @inject_plot_data により注入されます
        fig: 既存の Plotly Figure オブジェクト
        **kwargs: Plotly backend に渡す追加引数

    Returns:
        Any: Plotly Figure オブジェクト (ノートブック環境では自動的に表示される)
    """
    from ...visualization import backend_plotly
    
    # kwargsからnameを取り出す (優先) -> inject_plot_data has no knoweldge of 'y_name' anymore. 
    # Use title or y_label as generic name or extract from y_label?
    # y_label format is "Name [Unit]" or "Name".
    plot_name = kwargs.pop("name", y_label.split(" [")[0])

    return backend_plotly.plot(
        x_values=x_values,
        y_values=y_values,
        x_label=x_label,
        y_label=y_label,
        title=title,
        plot_type=kwargs.pop("plot_type", "scatter"), # Default handled in backend?
        fig=fig,
        name=plot_name,
        **kwargs
    )
