from typing import Optional, List, Any
import numpy as np
from ...operations.registry import operation
from ...domains.strain import StrainCollection

from ...visualization import backend_mpl

@operation(domain="strain")
def plot_rosette_vectors(
    collection: StrainCollection,
    rosette_name: str,
    step_index: int = 0,
    scale: float = 1.0,
    ax: Optional[Any] = None
) -> Any:
    """ロゼットの主ひずみベクトルをプロットする

    指定したステップにおける主ひずみ（最大・最小）の大きさと方向を、
    ロゼットの設置位置にベクトルとして描画します。
    (事前に calculate_rosette_strains を実行しておく必要があります)

    Args:
        collection: ひずみコレクション
        rosette_name: ロゼット名
        step_index: プロットするステップのインデックス
        scale: ベクトルの長さのスケール
        ax: MatplotlibのAxesオブジェクト（指定がない場合は新規作成）

    Returns:
        Axes: プロットされたAxesオブジェクト
    """

    # カラム名の推定
    prefix = rosette_name
    cols = {
        "e1": f"{prefix}_e1",
        "e2": f"{prefix}_e2",
        "theta": f"{prefix}_theta"
    }
    
    for key, col in cols.items():
        if col not in collection.columns:
            # 接頭辞が違う可能性も考慮すべきだが、一旦単純化
            # calculate_rosette_strains のデフォルト挙動に依存
            raise ValueError(f"計算済みカラム '{col}' が見つかりません。先に calculate_rosette_strains を実行してください。")

    # データ取得
    try:
        val_e1 = collection[cols["e1"]].values[step_index]
        val_e2 = collection[cols["e2"]].values[step_index]
        val_theta = collection[cols["theta"]].values[step_index]
        
        # 座標取得 (計算結果カラムに座標が引き継がれている前提)
        x, y, z = collection.get_column_coordinates(cols["e1"])
        if x is None or y is None:
             # ロゼット定義から座標取得を試みる
             rosette_info = collection.get_rosette(rosette_name)
             if rosette_info and "columns" in rosette_info:
                 x, y, z = collection.get_column_coordinates(rosette_info["columns"][0])
    except IndexError:
        raise ValueError(f"Step index {step_index} is out of range.")

    if x is None or y is None:
        raise ValueError(f"Coordinate data not found for rosette '{rosette_name}'.")

    # プロット準備
    # backend_mpl doesn't strictly abstract everything yet, so we use it for basic setup
    if ax is None:
        ax = backend_mpl.plot(x_values=[], y_values=[], title=f"Rosette: {rosette_name} (Step: {step_index})")
    
    # arrowはまだbackendにないので直接呼ぶか、追加したdraw_arrowを使う
    # backend_mpl.draw_arrow を使う
    
    # 角度をラジアンに
    theta_rad = np.radians(val_theta)
    
    # 主ひずみ1 (最大) のベクトル成分
    v1_x = val_e1 * np.cos(theta_rad) * scale
    v1_y = val_e1 * np.sin(theta_rad) * scale
    
    # 主ひずみ2 (最小) のベクトル成分 (theta + 90deg)
    v2_x = val_e2 * np.cos(theta_rad + np.pi/2) * scale
    v2_y = val_e2 * np.sin(theta_rad + np.pi/2) * scale
    
    # 描画
    # e1: Red arrows
    backend_mpl.draw_arrow(ax, x, y, v1_x, v1_y, head_width=scale*0.1, head_length=scale*0.1, fc='r', ec='r', label=f"e1: {val_e1:.2e}")
    backend_mpl.draw_arrow(ax, x, y, -v1_x, -v1_y, head_width=scale*0.1, head_length=scale*0.1, fc='r', ec='r')
    
    # e2: Blue arrows
    backend_mpl.draw_arrow(ax, x, y, v2_x, v2_y, head_width=scale*0.1, head_length=scale*0.1, fc='b', ec='b', label=f"e2: {val_e2:.2e}")
    backend_mpl.draw_arrow(ax, x, y, -v2_x, -v2_y, head_width=scale*0.1, head_length=scale*0.1, fc='b', ec='b')
    
    backend_mpl.scatter_points([x], [y], ax=ax, color='k', marker='o', s=25) # Center point
    
    ax.set_aspect('equal')
    ax.grid(True)
    backend_mpl.set_labels(ax, xlabel='X', ylabel='Y')
    
    return ax


@operation(domain="strain")
def iplot_rosette_vectors(
    collection: StrainCollection,
    rosette_name: str,
    step_index: int = 0,
    scale: float = 1.0,
    fig: Optional[Any] = None
) -> Any:
    """ロゼットの主ひずみベクトルをインタラクティブにプロットする (Plotly)"""
    from ...visualization import backend_plotly as plotly_backend
    
    # カラム名の推定 (plot_rosette_vectors と共通ロジックだが、一旦複製)
    # TODO: 共通化すべき
    prefix = rosette_name
    cols = {
        "e1": f"{prefix}_e1",
        "e2": f"{prefix}_e2",
        "theta": f"{prefix}_theta"
    }
    
    # データ取得
    try:
        val_e1 = collection[cols["e1"]].values[step_index]
        val_e2 = collection[cols["e2"]].values[step_index]
        val_theta = collection[cols["theta"]].values[step_index]
        
        # 座標取得
        x, y, z = collection.get_column_coordinates(cols["e1"])
        if x is None or y is None:
             rosette_info = collection.get_rosette(rosette_name)
             if rosette_info and "columns" in rosette_info:
                 x, y, z = collection.get_column_coordinates(rosette_info["columns"][0])
    except (IndexError, KeyError, ValueError):
        # エラーハンドリングは簡易的に
        raise ValueError(f"Data extraction failed for rosette '{rosette_name}' at step {step_index}")

    if x is None or y is None:
        raise ValueError(f"Coordinate data not found for rosette '{rosette_name}'.")

    if fig is None:
        fig = plotly_backend.create_figure()
        plotly_backend.set_labels(fig, title=f"Rosette: {rosette_name} (Step: {step_index})")

    # 角度をラジアンに
    theta_rad = np.radians(val_theta)
    
    # 主ひずみ1 (最大) のベクトル成分
    v1_x = val_e1 * np.cos(theta_rad) * scale
    v1_y = val_e1 * np.sin(theta_rad) * scale
    
    # 主ひずみ2 (最小) のベクトル成分 (theta + 90deg)
    v2_x = val_e2 * np.cos(theta_rad + np.pi/2) * scale
    v2_y = val_e2 * np.sin(theta_rad + np.pi/2) * scale
    
    # 描画 (Arrows)
    # e1: Red arrows
    plotly_backend.draw_arrow(fig, x, y, v1_x, v1_y, fc='red')
    plotly_backend.draw_arrow(fig, x, y, -v1_x, -v1_y, fc='red')
    
    # e2: Blue arrows
    plotly_backend.draw_arrow(fig, x, y, v2_x, v2_y, fc='blue')
    plotly_backend.draw_arrow(fig, x, y, -v2_x, -v2_y, fc='blue')
    
    # Center point
    plotly_backend.scatter_points([x], [y], fig=fig, name="Center", color="black")
    
    # Aspect ratio adjustment is tricky in plotly if generic, but usually:
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    
    return fig
