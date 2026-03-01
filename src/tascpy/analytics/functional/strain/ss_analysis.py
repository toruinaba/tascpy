import numpy as np
from typing import Tuple, Optional

def compute_stress(load_vals: np.ndarray, area: float) -> np.ndarray:
    """応力を計算する純粋関数

    Args:
        load_vals: 荷重配列
        area: 断面積

    Returns:
        np.ndarray: 応力配列
    """
    return load_vals / area

def compute_material_properties(
    stress: np.ndarray,
    strain: np.ndarray,
    lateral_strain: Optional[np.ndarray] = None,
    elastic_range: Tuple[float, float] = (0.0005, 0.0025),
    offset: float = 0.002
) -> Tuple[float, float, float, float]:
    """材料特性（ヤング率、降伏点、ポアソン比）を計算する純粋関数

    Args:
        stress: 応力配列
        strain: 縦ひずみ配列
        lateral_strain: 横ひずみ配列（オプション）
        elastic_range: ヤング率計算に使用するひずみ範囲
        offset: 耐力計算用のオフセットひずみ量

    Returns:
        Tuple[float, float, float, float]: (ヤング率 E, 降伏ひずみ, 降伏応力, ポアソン比 nu)
        計算できない場合は適宜 np.nan を返します
    """
    E = np.nan
    yield_strain = np.nan
    yield_stress = np.nan
    nu = np.nan

    # 共通の有効データインデックス
    mask = (~np.isnan(stress)) & (~np.isnan(strain))
    stress_valid = stress[mask]
    strain_valid = strain[mask]

    # 1. ヤング率 (Young's Modulus)
    e_start, e_end = elastic_range
    range_mask = (strain_valid >= e_start) & (strain_valid <= e_end)
    intercept = np.nan

    if np.sum(range_mask) > 2:
        E, intercept = np.polyfit(strain_valid[range_mask], stress_valid[range_mask], 1)

    # 2. 降伏強度 / 耐力 (Yield Strength, 0.2% offset)
    if not np.isnan(E):
        offset_stress = E * (strain_valid - offset) + intercept
        diff = stress_valid - offset_stress
        
        search_start_idx = np.where(strain_valid > e_end)[0]
        if len(search_start_idx) > 0:
            start_idx = search_start_idx[0]
            for i in range(start_idx, len(diff)-1):
                if diff[i] * diff[i+1] <= 0:
                    r = abs(diff[i]) / (abs(diff[i]) + abs(diff[i+1]))
                    yield_strain = strain_valid[i] + r * (strain_valid[i+1] - strain_valid[i])
                    yield_stress = stress_valid[i] + r * (stress_valid[i+1] - stress_valid[i])
                    break

    # 3. ポアソン比 (Poisson's Ratio)
    if lateral_strain is not None:
        lat_strain_valid = lateral_strain[mask]
        if np.sum(range_mask) > 2:
            slope_nu, _ = np.polyfit(strain_valid[range_mask], lat_strain_valid[range_mask], 1)
            nu = -slope_nu

    return E, yield_strain, yield_stress, nu
