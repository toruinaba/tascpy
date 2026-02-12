from typing import List, Optional, Tuple, Dict, Any, Union
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ...operations.registry import operation
from ...domains.strain import StrainCollection

@operation(domain="strain")
def plot_rosette_vectors(
    collection: StrainCollection,
    step_index: int = 0,
    rosette_names: Optional[List[str]] = None,
    scale: float = 1.0,
    figsize: Tuple[int, int] = (10, 8),
    title: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    show: bool = True
) -> Optional[plt.Figure]:
    """指定したステップにおける主ひずみベクトルをプロットする
    
    各ロゼットの位置(x, y)に、主ひずみの大きさと方向を表すベクトル（十字）を描画します。
    引張は赤、圧縮は青で表示します。
    
    Args:
        collection: StrainCollectionオブジェクト
        step_index: 表示する時間ステップのインデックス
        rosette_names: 表示するロゼット名のリスト（Noneの場合は全て）
        scale: ベクトルの表示倍率
        figsize: 図のサイズ
        title: タイトル
        ax: 描画対象のAxes（Noneの場合は新規作成）
        show: plt.show()を呼ぶかどうか
        
    Returns:
        Optional[plt.Figure]: 作成されたFigureオブジェクト（show=Falseの場合）
    """
    
    if rosette_names is None:
        rosette_names = collection.get_defined_rosettes()
        
    if not rosette_names:
        print("表示可能なロゼット定義がありません")
        return None
        
    # 図の準備
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # 全体の範囲計算用
    all_x = []
    all_y = []
    
    for r_name in rosette_names:
        # ロゼット情報を取得
        info = collection.get_rosette_info(r_name)
        gauge_cols = info["columns"]
        
        # 座標取得（第1ゲージの位置を代表点とする）
        x, y, z = collection.get_column_coordinates(gauge_cols[0])
        
        if x is None or y is None:
            print(f"ロゼット '{r_name}' に座標情報がありません (x={x}, y={y})")
            continue
            
        all_x.append(x)
        all_y.append(y)
        
        # 計算結果カラム名の推定（calculate_rosette_strainsで付けられる名前）
        # prefixが指定されていない場合はrosette_nameが使われる
        col_ep1 = f"{r_name}_epsilon1"
        col_ep2 = f"{r_name}_epsilon2"
        col_ang = f"{r_name}_angle"
        
        # カラムが存在するかチェック
        if col_ep1 not in collection.columns:
            print(f"ロゼット '{r_name}' の計算結果が見つかりません。calculate_rosette_strainsを実行してください。")
            continue
            
        # 値の取得
        ep1 = collection[col_ep1].values[step_index]
        ep2 = collection[col_ep2].values[step_index]
        angle_deg = collection[col_ang].values[step_index]
        
        if any(v is None or np.isnan(v) for v in [ep1, ep2, angle_deg]):
            continue
            
        # 角度をラジアンに変換
        # thetaは第1ゲージ軸（通常X軸と一致と仮定、orientationがあれば補正が必要）からの角度
        # ここではorientationはcalculate_rosette_strains内で考慮されていると仮定したいが、
        # 実際の実装を確認するとthetaはあくまでゲージ基準の角度。
        # ゲージ自体のorientation（配置角度）を足す必要がある。
        orientation = info.get("orientation", 0.0)
        global_angle_rad = np.radians(angle_deg + orientation)
        
        # ベクトルの描画 (Principal Strain 1)
        # 引張(正)なら赤、圧縮(負)なら青
        color1 = 'red' if ep1 >= 0 else 'blue'
        vec1_len = abs(ep1) * scale
        dx1 = vec1_len * np.cos(global_angle_rad)
        dy1 = vec1_len * np.sin(global_angle_rad)
        
        # 中心から両側に線を引く
        ax.plot([x - dx1, x + dx1], [y - dy1, y + dy1], color=color1, linewidth=2, label='Principal 1' if 'Principal 1' not in [l.get_label() for l in ax.get_lines()] else "")
        
        # ベクトルの描画 (Principal Strain 2) - 常に直交
        color2 = 'red' if ep2 >= 0 else 'blue'
        vec2_len = abs(ep2) * scale
        dx2 = vec2_len * np.cos(global_angle_rad + np.pi/2)
        dy2 = vec2_len * np.sin(global_angle_rad + np.pi/2)
        
        ax.plot([x - dx2, x + dx2], [y - dy2, y + dy2], color=color2, linewidth=2, label='Principal 2' if 'Principal 2' not in [l.get_label() for l in ax.get_lines()] else "")
        
        # ロゼット名の表示
        ax.text(x, y, r_name, fontsize=8, ha='right', va='bottom')

    # 軸の設定
    if all_x and all_y:
        # 余白を追加
        margin_x = (max(all_x) - min(all_x)) * 0.1 if max(all_x) != min(all_x) else 1.0
        margin_y = (max(all_y) - min(all_y)) * 0.1 if max(all_y) != min(all_y) else 1.0
        
        ax.set_xlim(min(all_x) - margin_x, max(all_x) + margin_x)
        ax.set_ylim(min(all_y) - margin_y, max(all_y) + margin_y)
        ax.set_aspect('equal')
        
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    
    if title:
        ax.set_title(title)
    else:
        step_val = collection.step.values[step_index]
        ax.set_title(f"Principal Strains at Step {step_index} (Value: {step_val})")
        
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # 凡例（重複排除済み）
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    if by_label:
        ax.legend(by_label.values(), by_label.keys())

    if show:
        plt.show()
        return None
    else:
        return fig
