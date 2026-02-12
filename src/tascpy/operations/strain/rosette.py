from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from ...operations.registry import operation
from ...domains.strain import StrainCollection
from ...core.column import Column

@operation(domain="strain")
def calculate_rosette_strains(
    collection: StrainCollection,
    rosette_name: str,
    result_prefix: Optional[str] = None
) -> StrainCollection:
    """3軸ロゼットひずみゲージから主ひずみなどを計算する
    
    以下の値を計算し、新しいカラムとして追加します：
    - 最大主ひずみ (epsilon_1)
    - 最小主ひずみ (epsilon_2)
    - 最大せん断ひずみ (gamma_max)
    - 主ひずみ方向 (epsilon_angle): 第1ゲージ軸からの角度 (deg)
    
    Args:
        collection: ひずみコレクション
        rosette_name: 定義済みのロゼット名
        result_prefix: 結果カラム名の接頭辞 (デフォルトはrosette_name)
        
    Returns:
        StrainCollection: 計算結果を含む新しいコレクション
    """
    
    # ロゼット情報を取得
    rosette_info = collection.get_rosette_info(rosette_name)
    gauge_cols = rosette_info["columns"]
    rosette_type = rosette_info.get("type", "rectangular")
    orientation = rosette_info.get("orientation", 0.0)
    
    # 接頭辞の決定
    prefix = result_prefix if result_prefix else rosette_name
    
    # データの取得
    e1 = collection[gauge_cols[0]].values
    e2 = collection[gauge_cols[1]].values
    e3 = collection[gauge_cols[2]].values
    
    # None対策: 全てfloatに変換し、NoneはNaNにする
    def to_array(data):
        return np.array([float(x) if x is not None else np.nan for x in data])
        
    e_a = to_array(e1)
    e_b = to_array(e2)
    e_c = to_array(e3)
    
    # 計算用バッファ
    n = len(e_a)
    ep1 = np.full(n, np.nan)
    ep2 = np.full(n, np.nan)
    gamma_max = np.full(n, np.nan)
    theta = np.full(n, np.nan)
    
    valid_mask = ~np.isnan(e_a) & ~np.isnan(e_b) & ~np.isnan(e_c)
    
    if np.any(valid_mask):
        ea_v = e_a[valid_mask]
        eb_v = e_b[valid_mask]
        ec_v = e_c[valid_mask]
        
        if rosette_type == "rectangular":
            # 0/45/90 rectangular rosette
            # center = (ea + ec) / 2
            # radius = sqrt(2)/2 * sqrt((ea - eb)^2 + (eb - ec)^2)
            center = (ea_v + ec_v) / 2.0
            radius = (np.sqrt(2.0) / 2.0) * np.sqrt((ea_v - eb_v)**2 + (eb_v - ec_v)**2)
            
            ep1[valid_mask] = center + radius
            ep2[valid_mask] = center - radius
            gamma_max[valid_mask] = 2.0 * radius
            
            # Angle calculation
            # tan(2*theta) = (2*eb - ea - ec) / (ea - ec)
            numerator = 2.0 * eb_v - ea_v - ec_v
            denominator = ea_v - ec_v
            
            # atan2 returns angle in radians between -pi and pi
            theta_rad = 0.5 * np.arctan2(numerator, denominator)
            theta_deg = np.degrees(theta_rad)
            theta[valid_mask] = theta_deg

        elif rosette_type == "delta":
            # 0/60/120 delta rosette
            # center = (ea + eb + ec) / 3
            # radius = sqrt(2)/3 * sqrt((ea - eb)^2 + (eb - ec)^2 + (ec - ea)^2)
            center = (ea_v + eb_v + ec_v) / 3.0
            term = (ea_v - eb_v)**2 + (eb_v - ec_v)**2 + (ec_v - ea_v)**2
            radius = (np.sqrt(2.0) / 3.0) * np.sqrt(term)
            
            ep1[valid_mask] = center + radius
            ep2[valid_mask] = center - radius
            gamma_max[valid_mask] = 2.0 * radius
            
            # Angle: tan(2*theta) = sqrt(3)*(ec - eb) / (2*ea - eb - ec)
            numerator = np.sqrt(3.0) * (ec_v - eb_v)
            denominator = 2.0 * ea_v - eb_v - ec_v
            
            theta_rad = 0.5 * np.arctan2(numerator, denominator)
            theta_deg = np.degrees(theta_rad)
            theta[valid_mask] = theta_deg
            
        else:
            raise ValueError(f"Unknown rosette type: {rosette_type}")

    # 結果コレクションの作成
    result = collection.clone()
    
    # 結果の単位 (入力と同じと仮定、ただし角度はdeg)
    unit = collection[gauge_cols[0]].unit if hasattr(collection[gauge_cols[0]], "unit") else ""
    
    # カラムの追加
    result.add_column(
        f"{prefix}_epsilon1", 
        Column(None, f"{prefix}_epsilon1", unit, ep1.tolist(), 
               metadata={"description": "Maximum principal strain"})
    )
    result.add_column(
        f"{prefix}_epsilon2", 
        Column(None, f"{prefix}_epsilon2", unit, ep2.tolist(),
               metadata={"description": "Minimum principal strain"})
    )
    result.add_column(
        f"{prefix}_gamma_max", 
        Column(None, f"{prefix}_gamma_max", unit, gamma_max.tolist(),
               metadata={"description": "Maximum shear strain"})
    )
    result.add_column(
        f"{prefix}_angle", 
        Column(None, f"{prefix}_angle", "deg", theta.tolist(),
               metadata={"description": "Principal strain direction (angle from gauge 1)"})
    )
    
    # 座標情報のコピー（重心として扱うか、第1ゲージの位置とするか。ここでは第1ゲージの位置を採用）
    if hasattr(collection, "get_column_coordinates"):
        # ベースとなる座標（第1ゲージ）
        x, y, z = collection.get_column_coordinates(gauge_cols[0])
        
        # 追加した全てのカラムに同じ座標を設定
        for col_name in [f"{prefix}_epsilon1", f"{prefix}_epsilon2", f"{prefix}_gamma_max", f"{prefix}_angle"]:
             result.set_column_coordinates(col_name, x, y, z)
             
    return result

