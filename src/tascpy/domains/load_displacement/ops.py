"""荷重-変位ドメインの操作"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Self, Tuple

import numpy as np

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.core.ops import CoreOps, to_float_array
from tascpy.core.ops_list import OpsList
from tascpy.core.result import ScalarResult
from tascpy.numeric.curve import compute_peaks_and_valleys, compute_slopes, compute_stiffness, compute_yield_point
from tascpy.numeric.hysteresis import (
    compute_cumulative_curve,
    compute_cycle_markers,
    compute_hysteresis_energy,
    compute_secant_stiffness,
    compute_skeleton_curve,
)

from .collection import LoadDisplacementCollection


class LoadDisplacementOps(CoreOps[LoadDisplacementCollection]):
    """荷重-変位コレクションの操作（汎用操作も全て利用可能）"""

    def _cycle_column(self, cycle_column: Optional[str]) -> str:
        if cycle_column is not None:
            self._column_values(cycle_column)
            return cycle_column
        for name in self._c.columns:
            if "cycle" in name.lower():
                return name
        raise KeyError(
            "サイクル列が指定されておらず、自動検出もできませんでした。"
            "事前に cycle_count() でサイクル列を作成するか、cycle_column を指定してください。"
        )

    def _ld_arrays(self) -> Tuple[np.ndarray, np.ndarray]:
        return self._c.displacement_data, self._c.load_data

    def _ld_unit(self, sep: str) -> Optional[str]:
        return self._compound_unit(self._c.load_column, self._c.displacement_column, sep)

    # ── 解析 ──────────────────────────────────

    def calculate_slopes(self, result_column: Optional[str] = None, unit: Optional[str] = None,
                         ch: Optional[str] = None) -> Self:
        """区間ごとの傾き (dP/dδ) を新しい列として追加します（単位は "荷重/変位"）"""
        return self._with_column(result_column or "slope_data", compute_slopes(*self._ld_arrays()), unit, ch,
                                 self._ld_unit("/"))

    def calculate_stiffness(self, range_start: float = 0.2, range_end: float = 0.8,
                            method: str = "linear_regression") -> Self:
        """最大荷重に対する比率で指定した範囲の剛性を計算し、結果 "stiffness" に格納します

        変位が変化しない区間があると計算に失敗するため、事前に
        `remove_consecutive_duplicates_across()` で重複を除くことを推奨します。

        Args:
            range_start: 範囲の開始比率
            range_end: 範囲の終了比率
            method: "linear_regression" または "secant"

        Examples:
            >>> stiffness = ld.ops.calculate_stiffness(0.1, 0.8).end().results["stiffness"]
            >>> round(stiffness.value, 1), stiffness.unit
            (40.0, 'kN/mm')
        """
        value = compute_stiffness(*self._ld_arrays(), range_start=range_start, range_end=range_end, method=method)
        return self._with_result(ScalarResult(name="stiffness", value=value, unit=self._ld_unit("/")))

    def find_yield_point(self, method: str = "offset", offset_value: float = 0.002, range_start: float = 0.1,
                         range_end: float = 0.3, factor: float = 0.33,
                         fail_silently: bool = False) -> Self:
        """降伏点を検出し、結果 "yield_point" (PointResult) に格納します

        初期剛性を最大荷重の range_start〜range_end の範囲から求め、
        - "offset": 初期剛性線を offset_value だけ平行移動した直線との交点
        - "general": 接線剛性が初期剛性 × factor を下回る点
        を降伏点とします。

        Examples:
            >>> pt = ld.ops.find_yield_point(method="offset", offset_value=0.5, range_start=0.1, range_end=0.8).end().results["yield_point"]
            >>> round(pt.x, 2), round(pt.y, 1), pt.x_unit, pt.y_unit
            (3.0, 100.0, 'mm', 'kN')
        """
        outcome = compute_yield_point(
            *self._ld_arrays(), method=method, offset_value=offset_value, range_start=range_start,
            range_end=range_end, factor=factor, fail_silently=fail_silently,
        )
        return self._with_point("yield_point", outcome, x_unit=self._c.displacement.unit, y_unit=self._c.load.unit)

    # ── サイクル ──────────────────────────────

    def cycle_count(self, column: Optional[str] = None, step: float = 0.5, result_column: Optional[str] = None,
                    unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """荷重の符号反転に基づくサイクル番号の列 ("{荷重列}_cycle") を追加します

        Args:
            column: 判定に使う列（省略時は荷重列）
            step: 符号反転1回あたりのサイクル番号の増分（0.5 なら正負の往復で 1 サイクル）
        """
        source = column or self._c.load_column
        markers = compute_cycle_markers(to_float_array(self._column_values(source)), step=step)
        return self._with_column(result_column or f"{source}_cycle", markers.tolist(), unit, ch, default_unit="")

    def split_by_cycles(self, cycle_column: Optional[str] = None) -> OpsList[Self]:
        """サイクル番号ごとに分割します（サイクル列は省略時に自動検出）"""
        return self.split_by_integers(self._cycle_column(cycle_column))

    def find_peaks_and_valleys(self, column: Optional[str] = None, distance: int = 1,
                               threshold: Optional[float] = None, result_column: Optional[str] = None,
                               unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """ピーク (1) / バレー (-1) / その他 (0) のマーカー列 "peak_valley" を追加します

        Args:
            column: 対象列（省略時は荷重列）
            distance: 隣接ピーク間の最小距離
            threshold: ピークとみなす閾値
        """
        values = self._c.load_data if column is None else to_float_array(self._column_values(column))
        flags = compute_peaks_and_valleys(values, distance=distance, threshold=threshold)
        return self._with_column(result_column or "peak_valley", flags, unit, ch, default_unit="")

    def _per_cycle(self, cycle_column: Optional[str],
                   func: Callable[[np.ndarray, np.ndarray], tuple],
                   outputs: List[Dict[str, Any]]) -> CoreOps[ColumnCollection]:
        name = self._cycle_column(cycle_column)
        markers = to_float_array(self._column_values(name))
        keys = list(dict.fromkeys(v for v in markers if not np.isnan(v)))
        rows = [func(self._c.displacement_data[markers == k], self._c.load_data[markers == k]) for k in keys]

        columns = {
            spec["name"]: Column(spec["name"], [row[i] for row in rows], unit=spec.get("unit"),
                                 attrs=spec.get("attrs"))
            for i, spec in enumerate(outputs)
        }
        steps = [int(k) if float(k).is_integer() else k for k in keys]
        return CoreOps(ColumnCollection(columns, step=steps, metadata=dict(self._c.metadata, grouped_by=name)))

    def analyze_hysteresis(self, cycle_column: Optional[str] = None) -> CoreOps[ColumnCollection]:
        """サイクルごとの履歴エネルギーと最大・最小荷重/変位を集計した表を返します

        戻り値のステップはサイクル番号、列は energy（単位は "荷重*変位"）/ max_load / min_load / max_disp / min_disp です。
        """
        load_unit, disp_unit = self._c.load.unit, self._c.displacement.unit
        return self._per_cycle(cycle_column, compute_hysteresis_energy, [
            {"name": "energy", "unit": self._ld_unit("*"), "attrs": {"description": "Hysteresis loop area"}},
            {"name": "max_load", "unit": load_unit},
            {"name": "min_load", "unit": load_unit},
            {"name": "max_disp", "unit": disp_unit},
            {"name": "min_disp", "unit": disp_unit},
        ])

    def analyze_stiffness_degradation(self, cycle_column: Optional[str] = None) -> CoreOps[ColumnCollection]:
        """サイクルごとの割線剛性を集計した表を返します（列: stiffness）"""
        return self._per_cycle(cycle_column, lambda d, p: (compute_secant_stiffness(d, p),), [
            {"name": "stiffness", "unit": self._ld_unit("/"), "attrs": {"description": "Secant stiffness"}},
        ])

    # ── 特殊曲線 ──────────────────────────────

    def create_skeleton_curve(self, cycle_column: Optional[str] = None, has_decrease: bool = False,
                              decrease_type: str = "envelope") -> Self:
        """スケルトン曲線を生成し、結果 "skeleton_curve" (XYSeriesResult) に格納します"""
        x, y = compute_skeleton_curve(*self._all_cycle_arrays(cycle_column), has_decrease=has_decrease,
                                      decrease_type=decrease_type)
        return self._with_curve("skeleton_curve", x, y, *self._curve_units())

    def create_cumulative_curve(self, cycle_column: Optional[str] = None) -> Self:
        """累積塑性変形-荷重曲線を生成し、結果 "cumulative_curve" (XYSeriesResult) に格納します"""
        x, y = compute_cumulative_curve(*self._all_cycle_arrays(cycle_column))
        return self._with_curve("cumulative_curve", x, y, *self._curve_units())

    def _curve_units(self) -> Tuple[Optional[str], Optional[str]]:
        return self._c.displacement.unit, self._c.load.unit

    def _all_cycle_arrays(self, cycle_column: Optional[str]):
        name = self._cycle_column(cycle_column)
        return self._c.displacement_data, self._c.load_data, to_float_array(self._column_values(name))
