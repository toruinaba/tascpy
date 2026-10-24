"""ひずみドメインの操作"""

from __future__ import annotations

from typing import List, Optional, Self

import numpy as np

from tascpy.core.ops import to_float_array
from tascpy.domains.coordinate.ops import CoordinateOps
from tascpy.numeric.curve import compute_yield_point
from tascpy.numeric.rosette import compute_rosette_strains

from .collection import StrainCollection


class StrainOps(CoordinateOps[StrainCollection]):
    """ひずみコレクションの操作（汎用操作・座標操作も全て利用可能）"""

    def _float_column(self, name: Optional[str], label: str) -> np.ndarray:
        if not name or name not in self._c:
            raise ValueError(f"{label} '{name}' が見つかりません")
        return to_float_array(self._column_values(name))

    def calculate_rosette_strains(self, rosette_name: Optional[str] = None, columns: Optional[List[str]] = None,
                                  rosette_type: str = "rectangular", orientation: float = 0.0,
                                  prefix: Optional[str] = None) -> Self:
        """3 軸ロゼットから主ひずみ・最大せん断ひずみ・主方向を計算し、列を追加します

        追加される列: "{prefix}_e1", "{prefix}_e2", "{prefix}_gamma", "{prefix}_theta"

        Args:
            rosette_name: 登録済みロゼット名（指定時は columns / rosette_type / orientation を上書き）
            columns: ゲージの列名 [e1, e2, e3]
            rosette_type: "rectangular" または "delta"
            orientation: 第 1 ゲージの角度（度、X 軸基準・反時計回り）
            prefix: 結果列の接頭辞（省略時は rosette_name または "rosette"）

        Examples:
            >>> result = strain.ops.calculate_rosette_strains("R1").end()
            >>> round(float(result["R1_e1"].values[1]), 1), result["R1_e1"].unit, result["R1_theta"].unit
            (101.7, 'ue', 'deg')
        """
        if rosette_name:
            info = self._c.get_rosette(rosette_name)
            if info:
                columns = info.get("columns", columns)
                rosette_type = info.get("type", rosette_type)
                orientation = info.get("orientation", orientation)
            prefix = prefix or rosette_name
        prefix = prefix or "rosette"

        if not columns or len(columns) != 3:
            raise ValueError("3つのひずみカラムを指定する必要があります")
        e1, e2, e3 = (self._float_column(c, "カラム") for c in columns)
        e_max, e_min, gamma_max, theta = compute_rosette_strains(
            e1, e2, e3, rosette_type=rosette_type, angle_offset=orientation,
        )

        result = self._c
        unit = self._unit_of(columns[0])
        x, y, z = self._c.get_column_coordinates(columns[0])
        for suffix, values, description in [
            ("e1", e_max, "Max Principal Strain"),
            ("e2", e_min, "Min Principal Strain"),
            ("gamma", gamma_max, "Max Shear Strain"),
            ("theta", theta, "Principal Direction Angle (deg)"),
        ]:
            name = f"{prefix}_{suffix}"
            result = result.with_column(
                name, values, unit="deg" if suffix == "theta" else unit,
                attrs={"description": description, "source_rosette": rosette_name or "manual"},
            ).with_coordinates(name, x, y, z)
        return self._next(result)

    def calculate_stress(self, load_column: str, area: float, result_column: str = "stress",
                         unit: str = "MPa") -> Self:
        """応力 = 荷重 / 断面積 を新しい列として追加します

        Examples:
            >>> strain.ops.calculate_stress(load_column="荷重", area=10.0, result_column="応力").end()["応力"].values
            array([ 0. ,  4. ,  8. , 10. , 11. , 11.5])
        """
        stress = self._float_column(load_column, "荷重カラム") / area
        result = self._c.with_column(
            result_column, stress, unit=unit,
            attrs={
                "description": f"Calculated Stress (Load: {load_column}, Area: {area})",
                "source_load": load_column,
                "area": area,
            },
        )
        return self._next(result)

    def find_yield_point(self, stress_column: str, strain_column: str, method: str = "offset",
                         offset_value: float = 0.002, range_start: float = 0.1, range_end: float = 0.3,
                         factor: float = 0.33, fail_silently: bool = False) -> Self:
        """応力-ひずみ関係から降伏点を検出し、結果 "yield_point" (x: ひずみ, y: 応力) に格納します

        アルゴリズムは荷重-変位ドメインの find_yield_point と同じです。
        """
        stress = self._float_column(stress_column, "応力カラム")
        strain = self._float_column(strain_column, "ひずみカラム")
        outcome = compute_yield_point(
            strain, stress, method=method, offset_value=offset_value,
            range_start=range_start, range_end=range_end, factor=factor,
            fail_silently=fail_silently,
        )
        return self._with_point("yield_point", outcome, x_unit=self._unit_of(strain_column),
                                y_unit=self._unit_of(stress_column))
