"""ひずみゲージのロゼット解析の純粋関数"""

from typing import Tuple

import numpy as np


def compute_rosette_strains(
    e1: np.ndarray,
    e2: np.ndarray,
    e3: np.ndarray,
    rosette_type: str = "rectangular",
    angle_offset: float = 0.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """ロゼットひずみゲージの値から主ひずみを計算します。
    
    Args:
        e1: 第1ゲージのひずみ配列
        e2: 第2ゲージのひずみ配列
        e3: 第3ゲージのひずみ配列
        rosette_type: ロゼットの種類（'rectangular': 0°/45°/90°、'delta': 0°/60°/120°）
        angle_offset: 第1ゲージの設置角度（度）
        
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            (最大主ひずみ, 最小主ひずみ, 最大せん断ひずみ, 主ひずみ方向角度)。
            角度は最大主ひずみの方向を、第1ゲージの方向から反時計回りに測った度数（angle_offset を加算）です。

    Examples:
        >>> from tascpy.numeric.rosette import compute_rosette_strains
        >>> import numpy as np
        >>> e1, e2, e3 = np.array([100]), np.array([200]), np.array([300])
        >>> compute_rosette_strains(e1, e2, e3, "rectangular")  # 最大主ひずみ 300 は第3ゲージ（90°）の方向
        (array([300.]), array([100.]), array([200.]), array([90.]))
    """
    if rosette_type.lower() == "rectangular":
        ex = e1
        ey = e3
        gamma_xy = 2 * e2 - (e1 + e3)
    elif rosette_type.lower() == "delta":
        ex = e1
        ey = (2 * e2 + 2 * e3 - e1) / 3.0
        gamma_xy = (2.0 / np.sqrt(3.0)) * (e2 - e3)
    else:
        raise ValueError(f"未対応のロゼットの種類です: {rosette_type}（'rectangular', 'delta' のいずれか）")

    center = (ex + ey) / 2.0
    radius = np.sqrt(((ex - ey) / 2.0) ** 2 + (gamma_xy / 2.0) ** 2)
    
    e_max = center + radius
    e_min = center - radius
    gamma_max = 2 * radius
    
    theta_rad = 0.5 * np.arctan2(gamma_xy, ex - ey)
    theta_deg = np.degrees(theta_rad)
    final_theta = theta_deg + angle_offset
    
    return e_max, e_min, gamma_max, final_theta
