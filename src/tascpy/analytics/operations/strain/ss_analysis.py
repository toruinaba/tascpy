from typing import Optional, List, Any, Dict, Union, Tuple
import numpy as np

from ...operations.registry import register_functional
from tascpy.domains.strain import StrainCollection
from tascpy.core.column import Column
from tascpy.core.result import ScalarResult, PointResult
from ...operations.validation import requires_column
from ...functional.strain.ss_analysis import compute_stress, compute_material_properties
from ...operations.abstraction import store_multiple_results
from .abstraction import resolve_stress_calculation, resolve_stress_strain

calculate_stress = register_functional(
    compute_stress,
    domain="strain",
    name="calculate_stress",
    extra_decorators=[resolve_stress_calculation()]
)
"""応力を計算する (Stress = Load / Area)

    Args:
        collection: ひずみコレクション
        load_column: 荷重データのカラム名
        area: 断面積
        result_column: 結果を格納するカラム名
        unit: 結果の単位

    Returns:
        StrainCollection: 応力カラムが追加されたコレクション
        
    Examples:
        >>> col = col.ops.calculate_stress(load_column="荷重", area=10.0, result_column="応力")
"""
calculate_stress.__doc__ = """応力を計算する (Stress = Load / Area)

    Args:
        collection: ひずみコレクション
        load_column: 荷重データのカラム名
        area: 断面積
        result_column: 結果を格納するカラム名
        unit: 結果の単位

    Returns:
        StrainCollection: 応力カラムが追加されたコレクション
        
    Examples:
        >>> col = col.ops.calculate_stress(load_column="荷重", area=10.0, result_column="応力")
"""

analyze_material_properties = register_functional(
    compute_material_properties,
    domain="strain",
    name="analyze_material_properties",
    extra_decorators=[
        resolve_stress_strain(),
        store_multiple_results(
            results=[
                {
                    "type": "scalar", 
                    "name": "{result_prefix}_E", 
                    "index": 0, 
                    "metadata": {"description": "Young's Modulus"}
                },
                {
                    "type": "point", 
                    "name": "{result_prefix}_yield", 
                    "x_index": 1, 
                    "y_index": 2, 
                    "metadata": {"description": "Offset Yield Strength"}
                },
                {
                    "type": "scalar", 
                    "name": "{result_prefix}_nu", 
                    "index": 3, 
                    "metadata": {"description": "Poisson's Ratio"}
                }
            ]
        )
    ]
)
"""材料特性（ヤング率、降伏点、ポアソン比）を解析する

    Args:
        collection: ひずみコレクション
        stress_column: 応力カラム名
        strain_column: ひずみ（縦）カラム名
        lateral_strain_column: 横ひずみカラム名（ポアソン比計算用、任意）
        elastic_range: ヤング率計算に使用するひずみ範囲 (start, end)
        offset: 耐力計算用のオフセットひずみ量 (デフォルト 0.002 = 0.2%)
        result_prefix: 結果名の接頭辞

    Returns:
        Tuple: E, yield_strain, yield_stress, nu
        
    Examples:
        >>> col = col.ops.analyze_material_properties(
        ...     stress_column="応力", strain_column="CH1", elastic_range=(0.0, 0.001)
        ... )
        >>> youngs_modulus = col.results["youngs_E"].value
"""
analyze_material_properties.__doc__ = """材料特性（ヤング率、降伏点、ポアソン比）を解析する

    Args:
        collection: ひずみコレクション
        stress_column: 応力カラム名
        strain_column: ひずみ（縦）カラム名
        lateral_strain_column: 横ひずみカラム名（ポアソン比計算用、任意）
        elastic_range: ヤング率計算に使用するひずみ範囲 (start, end)
        offset: 耐力計算用のオフセットひずみ量 (デフォルト 0.002 = 0.2%)
        result_prefix: 結果名の接頭辞

    Returns:
        Tuple: E, yield_strain, yield_stress, nu
        
    Examples:
        >>> col = col.ops.analyze_material_properties(
        ...     stress_column="応力", strain_column="CH1", elastic_range=(0.0, 0.001)
        ... )
        >>> youngs_modulus = col.results["youngs_E"].value
"""

