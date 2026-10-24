from typing import Any, Optional

from tascpy.numeric.rosette import compute_rosette_vectors
from tascpy.core.plot.draw import new_axes


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
        
    Examples:
        >>> from tascpy.visualization.functional.strain.plot import plot_rosette_vectors
        >>> ax = plot_rosette_vectors(x=0.0, y=0.0, e1=1000e-6, e2=-500e-6, theta=0.785, rosette_name="R1")
    """
    if ax is None:
        ax = new_axes()
        ax.set_title(f"Rosette: {rosette_name} (Step: {step_index})")

    v1_x, v1_y, v2_x, v2_y = compute_rosette_vectors(e1, e2, theta, scale)
    head = {"head_width": scale * 0.1, "head_length": scale * 0.1}
    ax.arrow(x, y, v1_x, v1_y, fc="r", ec="r", label=f"e1: {e1:.2e}", **head)
    ax.arrow(x, y, -v1_x, -v1_y, fc="r", ec="r", **head)
    ax.arrow(x, y, v2_x, v2_y, fc="b", ec="b", label=f"e2: {e2:.2e}", **head)
    ax.arrow(x, y, -v2_x, -v2_y, fc="b", ec="b", **head)
    ax.scatter([x], [y], color="k", marker="o", s=25)

    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
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
    fig: Any = None
) -> Any:
    """ロゼットの主ひずみベクトルをインタラクティブにプロットする (Plotly)
    
    Examples:
        >>> from tascpy.visualization.functional.strain.plot import iplot_rosette_vectors
        >>> fig = iplot_rosette_vectors(x=0.0, y=0.0, e1=1000e-6, e2=-500e-6, theta=0.785, rosette_name="R1")
    """
    from tascpy.core.plot import plotly_backend
    
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
