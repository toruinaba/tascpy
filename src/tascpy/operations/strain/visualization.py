from typing import Optional, List, Any
import numpy as np
from ...operations.registry import operation
from ...domains.strain import StrainCollection

try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

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
    if not HAS_MATPLOTLIB:
        raise ImportError("Matplotlib is required for plotting.")

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
    if ax is None:
        fig, ax = plt.subplots()
    
    # 角度をラジアンに
    theta_rad = np.radians(val_theta)
    
    # 主ひずみ1 (最大) のベクトル成分
    # 2方向に伸びるので、中心から +/- 方向に描画
    v1_x = val_e1 * np.cos(theta_rad) * scale
    v1_y = val_e1 * np.sin(theta_rad) * scale
    
    # 主ひずみ2 (最小) のベクトル成分 (theta + 90deg)
    v2_x = val_e2 * np.cos(theta_rad + np.pi/2) * scale
    v2_y = val_e2 * np.sin(theta_rad + np.pi/2) * scale
    
    # 描画
    # e1: Red arrows
    ax.arrow(x, y, v1_x, v1_y, head_width=scale*0.1, head_length=scale*0.1, fc='r', ec='r', label=f"e1: {val_e1:.2e}")
    ax.arrow(x, y, -v1_x, -v1_y, head_width=scale*0.1, head_length=scale*0.1, fc='r', ec='r')
    
    # e2: Blue arrows
    ax.arrow(x, y, v2_x, v2_y, head_width=scale*0.1, head_length=scale*0.1, fc='b', ec='b', label=f"e2: {val_e2:.2e}")
    ax.arrow(x, y, -v2_x, -v2_y, head_width=scale*0.1, head_length=scale*0.1, fc='b', ec='b')
    
    ax.plot(x, y, 'ko', markersize=5) # Center point
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title(f"Rosette: {rosette_name} (Step: {step_index})")
    
    return ax
