from typing import Optional, Any
import numpy as np

from tascpy.visualization import backend_mpl
from tascpy.analytics.functional.strain.rosette import compute_rosette_vectors


def plot_rosette_vectors(
    x: float,
    y: float,
    e1: float,
    e2: float,
    theta: float,
    rosette_name: str,
    step_index: int = 0,
    scale: float = 1.0,
    ax: Optional[Any] = None
) -> Any:
    """ロゼットの主ひずみベクトルをプロットします

    指定したステップにおける主ひずみ（最大・最小）の大きさと方向を、
    ロゼットの設置位置にベクトルとして描画します。

    Args:
        x: ロゼットのX座標
        y: ロゼットのY座標
        e1: 主ひずみ1 (最大主ひずみ)
        e2: 主ひずみ2 (最小主ひずみ)
        theta: 主ひずみ方向角度 (ラジアンまたは度、compute_rosette_vectorsの仕様に依存)
        rosette_name: ロゼット名 (タイトル表示用)
        step_index: ステップインデックス (タイトル表示用)
        scale: ベクトルの長さのスケール
        ax: MatplotlibのAxesオブジェクト（指定がない場合は新規作成）

    Returns:
        Axes: プロットされたAxesオブジェクト
    """
    # 描画準備
    if ax is None:
        ax = backend_mpl.plot(x_values=[], y_values=[], title=f"Rosette: {rosette_name} (Step: {step_index})")
    
    # 純粋関数を呼び出してベクトル成分を取得
    v1_x, v1_y, v2_x, v2_y = compute_rosette_vectors(e1, e2, theta, scale)
    
    # e1: Red arrows
    backend_mpl.draw_arrow(ax, x, y, v1_x, v1_y, head_width=scale*0.1, head_length=scale*0.1, fc='r', ec='r', label=f"e1: {e1:.2e}")
    backend_mpl.draw_arrow(ax, x, y, -v1_x, -v1_y, head_width=scale*0.1, head_length=scale*0.1, fc='r', ec='r')
    
    # e2: Blue arrows
    backend_mpl.draw_arrow(ax, x, y, v2_x, v2_y, head_width=scale*0.1, head_length=scale*0.1, fc='b', ec='b', label=f"e2: {e2:.2e}")
    backend_mpl.draw_arrow(ax, x, y, -v2_x, -v2_y, head_width=scale*0.1, head_length=scale*0.1, fc='b', ec='b')
    
    # Center point
    backend_mpl.scatter_points([x], [y], ax=ax, color='k', marker='o', s=25)
    
    ax.set_aspect('equal')
    ax.grid(True)
    backend_mpl.set_labels(ax, xlabel='X', ylabel='Y')
    
    return ax


def iplot_rosette_vectors(
    x: float,
    y: float,
    e1: float,
    e2: float,
    theta: float,
    rosette_name: str,
    step_index: int = 0,
    scale: float = 1.0,
    fig: Optional[Any] = None
) -> Any:
    """ロゼットの主ひずみベクトルをインタラクティブにプロットする (Plotly)"""
    from tascpy.visualization import backend_plotly as plotly_backend
    
    if fig is None:
        fig = plotly_backend.create_figure()
        plotly_backend.set_labels(fig, title=f"Rosette: {rosette_name} (Step: {step_index})")

    # 純粋関数を呼び出してベクトル成分を取得
    v1_x, v1_y, v2_x, v2_y = compute_rosette_vectors(e1, e2, theta, scale)
    
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
