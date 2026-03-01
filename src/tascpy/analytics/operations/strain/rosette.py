from typing import List, Optional, Union
import numpy as np

from ...operations.registry import register_functional
from tascpy.domains.strain import StrainCollection
from ...functional.strain.rosette import compute_rosette_strains
from .abstraction import resolve_rosette_strains

calculate_rosette_strains = register_functional(
    compute_rosette_strains,
    domain="strain",
    name="calculate_rosette_strains",
    extra_decorators=[resolve_rosette_strains()]
)
calculate_rosette_strains.__doc__ = """ロゼットひずみ計算 (主ひずみ・主応力方向)

    3軸ひずみゲージの値から、最大・最小主ひずみ、最大せん断ひずみ、主ひずみ方向を計算します。

    Args:
        collection: ひずみコレクション
        rosette_name: 定義済みのロゼット名（metadataから情報を取得）
        columns: ゲージのカラム名リスト [e1, e2, e3]。
                 rosette_name指定時は無視されます。
                 直交の場合: 0, 45, 90度
                 デルタの場合: 0, 60, 120度
        rosette_type: ロゼットタイプ ('rectangular' or 'delta')
                      rosette_name指定時はmetadataが優先されます。
        orientation: 第1ゲージの設置角度（X軸基準、反時計回り、度単位）
                     rosette_name指定時はmetadataが優先されます。
        prefix: 結果カラム名の接頭辞。デフォルトは rosette_name または "rosette"

    Returns:
        StrainCollection: 計算結果（e_max, e_min, gamma_max, theta）が追加されたコレクション
"""

