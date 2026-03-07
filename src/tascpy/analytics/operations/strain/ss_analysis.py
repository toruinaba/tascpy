from typing import Optional, List, Any, Dict, Union, Tuple
import numpy as np

from ...operations.registry import register_functional
from tascpy.domains.strain import StrainCollection
from tascpy.core.column import Column
from tascpy.core.result import ScalarResult, PointResult
from ...operations.validation import requires_column
from ...functional.strain.ss_analysis import compute_stress
from .abstraction import resolve_stress_calculation

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

from ...operations.abstraction import store_multiple_results
from ...functional.load_displacement.analysis import compute_yield_point
from .abstraction import resolve_stress_strain

find_yield_point = register_functional(
    compute_yield_point,
    domain="strain",
    name="find_yield_point",
    extra_decorators=[
        resolve_stress_strain(),
        store_multiple_results(
            results=[
                {
                    "type": "point", 
                    "name": "{result_prefix}_yield", 
                    "x_index": 1, 
                    "y_index": 2, 
                    "metadata": {"description": "Yield Point (Strain, Stress)"}
                }
            ]
        )
    ]
)
"""応力-ひずみデータから降伏点（Yield Point）を検出します。

    load_displacementドメインのfind_yield_pointと同様のアルゴリズムを使用しますが、
    応力(Load相当)とひずみ(Disp相当)を入力とします。

    Args:
        collection: ひずみコレクション
        stress_column: 応力データのカラム名（None時は自動解決または順序）
        strain_column: ひずみデータのカラム名（None時は自動解決または順序）
        method (str, optional): 降伏点判定手法 ("offset", "general"). Defaults to "offset".
        offset_value (float, optional): オフセット法におけるオフセットひずみ等. Defaults to 0.002.
        range_start (float, optional): 剛性計算の開始比率. Defaults to 0.1.
        range_end (float, optional): 剛性計算の終了比率. Defaults to 0.3.
        factor (float, optional): 特定手法での係数. Defaults to 0.33.
        debug_mode (bool, optional): デバッグ情報を表示するか. Defaults to False.
        fail_silently (bool, optional): 検出失敗時に例外を投げず無視するか. Defaults to False.
        result_prefix: 結果名の接頭辞
        
    Returns:
        StrainCollection: 降伏点情報が結果として追加された新しいコレクション
        
    Examples:
        >>> col = col.ops.find_yield_point(stress_column="応力", strain_column="CH1", method="offset", offset_value=0.002)
        >>> yield_pt = col.results["yield_yield"].value
"""
find_yield_point.__doc__ = """応力-ひずみデータから降伏点（Yield Point）を検出します。

    load_displacementドメインのfind_yield_pointと同様のアルゴリズムを使用しますが、
    応力(Load相当)とひずみ(Disp相当)を入力とします。

    Args:
        collection: ひずみコレクション
        stress_column: 応力データのカラム名（None時は自動解決または順序）
        strain_column: ひずみデータのカラム名（None時は自動解決または順序）
        method (str, optional): 降伏点判定手法 ("offset", "general"). Defaults to "offset".
        offset_value (float, optional): オフセット法におけるオフセットひずみ等. Defaults to 0.002.
        range_start (float, optional): 剛性計算の開始比率. Defaults to 0.1.
        range_end (float, optional): 剛性計算の終了比率. Defaults to 0.3.
        factor (float, optional): 特定手法での係数. Defaults to 0.33.
        debug_mode (bool, optional): デバッグ情報を表示するか. Defaults to False.
        fail_silently (bool, optional): 検出失敗時に例外を投げず無視するか. Defaults to False.
        result_prefix: 結果名の接頭辞
        
    Returns:
        StrainCollection: 降伏点情報が結果として追加された新しいコレクション
        
    Examples:
        >>> col = col.ops.find_yield_point(stress_column="応力", strain_column="CH1", method="offset", offset_value=0.002)
        >>> yield_pt = col.results["yield_yield"].value
"""

yield_point = find_yield_point
yield_point.__doc__ = "find_yield_point のエイリアス"
