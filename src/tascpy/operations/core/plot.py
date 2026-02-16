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

from ...operations.registry import operation
from ..abstraction import inject_plot_data, inject_columns
from .stats import detect_outliers
from .filters import filter_by_value


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
@inject_plot_data(x_arg="x_column", y_arg="column", positional_order=["column", "x_column"])
def visualize_outliers(
    x_values: Any,
    y_values: Any,
    x_label: str,
    y_label: str,
    title: str,
    window_size: int = 3,
    threshold: float = 0.5,
    highlight_color: str = "red",
    plot_type: str = "scatter",
    show_normal: bool = True,
    normal_color: str = "blue",
    normal_alpha: float = 0.5,
    outlier_marker: str = "o",
    outlier_size: int = 50,
    ax: Optional[plt.Axes] = None,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
    **kwargs
) -> plt.Axes:
    """異常値を可視化します（純粋関数版）

    Args:
        x_values: X軸のデータ（@inject_plot_dataにより注入）
        y_values: Y軸のデータ（@inject_plot_dataにより注入）
        x_label: X軸ラベル
        y_label: Y軸ラベル
        title: グラフタイトル
        window_size: 移動平均のウィンドウサイズ
        threshold: 異常値判定の閾値
        show_normal: 正常値を表示するかどうか
        ax: 既存のAxes
        ... (他パラメータ)

    Returns:
        plt.Axes: プロットオブジェクト
    """
    # 異常値検出の実行 (detect_outliersは純粋関数として呼び出し可能)
    # detect_outliersは @transform_column でラップされており、生データを受け取ると純粋関数として振る舞う
    # result_namingなどは無視される（コレクションを返さないため）
    flags = detect_outliers(
        y_values,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )
    
    # フラグに基づきデータを分割
    # flagsはList[int]なのでnumpy配列に変換
    flags_arr = np.array(flags)
    x_arr = np.array(x_values)
    y_arr = np.array(y_values)
    
    # 配列長チェックはdetect_outliers内で行われるが、ここでも安全のため確認
    if len(flags_arr) != len(x_arr) or len(flags_arr) != len(y_arr):
        # detect_outliersの実装依存だが、通常は一致するはず
        pass

    normal_mask = (flags_arr == 0)
    outlier_mask = (flags_arr == 1)
    
    outlier_count = np.sum(outlier_mask)

    # 新しい図を作成するか、既存のAxesを使用する
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # タイトルのオーバーライド
    if title.startswith("Outlier"): # デフォルトタイトル生成ロジックと重複しないように
         pass
    else:
         # inject_plot_dataが生成したタイトルを使用するが、異常値検知用にカスタマイズしたい場合
         # Kwargsでtitleが指定されていればそれが使われる
         pass
         
    # デフォルトタイトルを "Outlier detection of {y_name}" にしたい場合
    # inject_plot_dataは "Scatter plot of Y vs X" を生成して渡してくる
    # ここで上書きするか？
    # ユーザーが明示的に title を指定していない場合のみ上書きしたいが、
    # inject_plot_data は常に title を渡してくる。
    # kwargsに title があれば inject_plot_data はそれを使う。
    # なので、純粋関数の引数 title は常に値を持つ。
    # ここではそのまま使うことにする。

    if show_normal:
        plot_kwargs = kwargs.copy()
        plot_kwargs["color"] = normal_color
        plot_kwargs["alpha"] = normal_alpha
        # 明示的にplot_typeを渡す（デフォルトはscatter）
        plot_kwargs["plot_type"] = plot_type
        
        # 正常値をプロット
        # x_arr[normal_mask] が空でも plot はエラーにならない（空のプロットになる）
        plot(
            x_values=x_arr[normal_mask],
            y_values=y_arr[normal_mask],
            x_label=x_label,
            y_label=y_label,
            title=title,
            ax=ax,
            **plot_kwargs
        )

    # 異常値のプロット
    if outlier_count > 0:
        print(f"visualize_outliers: {outlier_count}個の異常値をプロットします")
        
        outlier_kwargs = {
            "color": highlight_color,
            "plot_type": "scatter",
            "s": outlier_size,
            "marker": outlier_marker,
            "label": "異常値",
            "zorder": 10,
        }
        
        # デバッグ出力
        out_x = x_arr[outlier_mask]
        out_y = y_arr[outlier_mask]
        if len(out_x) > 0:
            debug_count = min(3, len(out_x))
            print(f"最初の{debug_count}個の異常値データ: {list(zip(out_x[:debug_count], out_y[:debug_count]))}")

        plot(
            x_values=out_x,
            y_values=out_y,
            x_label=x_label,
            y_label=y_label,
            title=title,
            ax=ax,
            **outlier_kwargs
        )
    else:
        print("visualize_outliers: 異常値は検出されませんでした")
        # 正常値のみプロット済み
        
    # 異常値の数をタイトルに表示
    # y_labelから列名を取得 (例: "Temperature [C]" -> "Temperature")
    y_name_for_title = y_label.split(" [")[0]
    ax.set_title(f"異常値検出: {y_name_for_title} (検出数: {outlier_count}個)")

    # 凡例を表示（異常値があるか、正常値を表示している場合）
    if show_normal or outlier_count > 0:
        ax.legend()

    # グリッド線を追加して読みやすくする
    ax.grid(True, alpha=0.3)

    # 新しい図を作成した場合のみグラフを表示 (純粋関数なのでplt.show()は呼ばない)
    # if created_new_figure:
    #     plt.show()

    # 異常値検出結果を含むコレクションを返す
    # 純粋関数なのでAxesを返す
    return ax


@operation(domain="core")
@inject_columns(columns_arg="y_columns", columns_arg_pos=1)
def plot_const_x(
    y_data: Dict[str, Any],
    x_values: List[float],
    # y_columns (list of names) は inject_columns によって y_data (dict) に置換され、第一引数として渡される
    show_legend: bool = True,
    ax: Optional[plt.Axes] = None,
    **kwargs
) -> plt.Axes:
    """特定のx値に対して複数のy列の値をプロットします（純粋関数版）

    Args:
        y_data: {列名: 値配列} の辞書 (@inject_columnsにより注入)
        x_values: X軸の値のリスト
        show_legend: 凡例を表示するかどうか
        ax: 既存のAxes
        **kwargs: プロット関数に渡すキーワード引数

    Returns:
        plt.Axes: プロットオブジェクト
    """
    if len(x_values) != len(y_data):
        raise ValueError(f"x_valuesの長さ({len(x_values)})とy_columnsの長さ({len(y_data)})が一致しません")

    # 値を取得 (単一行を想定)
    # y_dataは辞書。キーの順序はy_columnsの順序と一致すると仮定(Python 3.7+ spec)
    y_vals_list = []
    
    for col_vals in y_data.values():
        # transform_column/inject_columns は値を配列(numpy or list)として抽出しているはず
        # スカラー値を取得
        if hasattr(col_vals, '__len__') and len(col_vals) > 0:
            val = col_vals[0]
            y_val = float(val) if val is not None else float('nan')
        elif np.isscalar(col_vals):
             y_val = float(col_vals)
        else:
             y_val = float('nan')
             
        y_vals_list.append(y_val)

    # NumPy配列に変換
    x_arr = np.array(x_values)
    y_arr = np.array(y_vals_list)

    # プロット
    x_label = kwargs.pop("x_label", "X Parameters")
    y_label = kwargs.pop("y_label", "Y Values")
    title = kwargs.pop("title", f"Plot of {len(y_data)} columns vs X")
    
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
