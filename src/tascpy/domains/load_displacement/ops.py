"""荷重-変位ドメインの操作"""

from __future__ import annotations

from typing import Optional, Self, Tuple

import numpy as np

from tascpy.core.collection import ColumnCollection
from tascpy.core.ops import CoreOps, to_float_array
from tascpy.core.ops_list import OpsList
from tascpy.core.result import PointResult, ScalarResult
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

    def _cycle_markers(self, cycle_column: Optional[str]) -> np.ndarray:
        """サイクル番号の配列（cycle_column の省略時は荷重の符号反転から数える。mark_cycles の既定と同じ）"""
        if cycle_column is None:
            return compute_cycle_markers(self._c.load_data)
        return to_float_array(self._column_values(cycle_column))

    def _ld_arrays(self) -> Tuple[np.ndarray, np.ndarray]:
        return self._c.displacement_data, self._c.load_data

    def _ld_unit(self, sep: str) -> Optional[str]:
        return self._compound_unit(self._c.load_column, self._c.displacement_column, sep)

    # ── 解析 ──────────────────────────────────

    def calculate_slopes(self, *, result_column: str, unit: Optional[str] = None,
                         ch: Optional[str] = None) -> Self:
        """区間ごとの傾き (dP/dδ) を新しい列として追加します（単位は "荷重/変位"）"""
        return self._with_column(result_column, compute_slopes(*self._ld_arrays()), unit, ch,
                                 self._ld_unit("/"))

    def stiffness(self, *, range_start: float = 0.2, range_end: float = 0.8,
                  method: str = "linear_regression") -> ScalarResult:
        """最大荷重に対する比率で指定した範囲の剛性を求めます（単位は "荷重/変位"）

        変位が変化しない区間があると計算に失敗するため、事前に
        `remove_consecutive_duplicates_across()` で重複を除くことを推奨します。

        単調載荷の曲線を前提にしています。繰り返し載荷のデータにそのまま使うと、範囲に入る除荷途中の点も
        計算に含まれ、エラーにならずに誤った値になります。`to_skeleton_curve()` でスケルトン曲線にするか、
        最初の載荷区間を抜き出してから求めてください。

        Args:
            range_start: 範囲の開始比率
            range_end: 範囲の終了比率
            method: "linear_regression" または "secant"

        Examples:
            >>> k = ld.ops.stiffness(range_start=0.1, range_end=0.8)
            >>> round(k.value, 1), k.unit
            (40.0, 'kN/mm')

            繰り返し載荷のデータ（`cyclic`）では、スケルトン曲線から求めます。

            >>> round(cyclic.ops.stiffness(range_start=0.1, range_end=0.5).value, 1)  # 生データのまま（誤り）
            8.6
            >>> round(cyclic.ops.to_skeleton_curve().stiffness(range_start=0.1, range_end=0.5).value, 1)
            40.0
        """
        value = compute_stiffness(*self._ld_arrays(), range_start=range_start, range_end=range_end, method=method)
        return ScalarResult(name="stiffness", value=value, unit=self._ld_unit("/"))

    def yield_point(self, *, method: str = "offset", offset_value: float = 0.002, range_start: float = 0.1,
                    range_end: float = 0.3, factor: float = 0.33, fail_silently: bool = False) -> PointResult:
        """降伏点を求めます（x: 変位, y: 荷重。metadata に is_valid と計算条件）

        初期剛性を最大荷重の range_start〜range_end の範囲から求め、
        - "offset": 初期剛性線を offset_value だけ平行移動した直線との交点
        - "general": 接線剛性が初期剛性 × factor を下回る点
        を降伏点とします。

        単調載荷の曲線を前提にしています（`stiffness` と同じ）。繰り返し載荷のデータでは、
        `to_skeleton_curve()` でスケルトン曲線にしてから求めてください。

        Examples:
            >>> pt = ld.ops.yield_point(offset_value=0.5, range_start=0.1, range_end=0.8)
            >>> round(pt.x, 2), round(pt.y, 1), pt.x_unit, pt.y_unit
            (3.0, 100.0, 'mm', 'kN')

            繰り返し載荷のデータ（`cyclic`）では、スケルトン曲線から求めます。

            >>> pt = cyclic.ops.to_skeleton_curve().yield_point(offset_value=0.5, range_start=0.1, range_end=0.5)
            >>> round(pt.x, 2), round(pt.y, 1)
            (3.06, 102.2)
        """
        outcome = compute_yield_point(
            *self._ld_arrays(), method=method, offset_value=offset_value, range_start=range_start,
            range_end=range_end, factor=factor, fail_silently=fail_silently,
        )
        return self._point("yield_point", outcome, x_unit=self._c.displacement.unit, y_unit=self._c.load.unit)

    # ── サイクル ──────────────────────────────

    def mark_cycles(self, *, column: Optional[str] = None, step: float = 0.5, result_column: str,
                    unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """荷重の符号反転に基づくサイクル番号の列を追加します

        サイクルを使う操作（`to_skeleton_curve` など）は cycle_column の省略時に同じ規則でサイクルを数えるため、
        この列は既定と異なる数え方をしたいときや、サイクル番号を列として使いたいときに作ります。

        Args:
            column: 判定に使う列（省略時は荷重列）
            step: 符号反転1回あたりのサイクル番号の増分（0.5 なら正負の往復で 1 サイクル）
        """
        source = column or self._c.load_column
        markers = compute_cycle_markers(to_float_array(self._column_values(source)), step=step)
        return self._with_column(result_column, markers.tolist(), unit, ch, default_unit="")

    def split_by_cycles(self, *, cycle_column: Optional[str] = None) -> OpsList[Self]:
        """サイクル番号ごとに分割します（cycle_column の省略時は荷重の符号反転から数える）"""
        return self.split_by_integers(self._cycle_markers(cycle_column))

    def mark_peaks_and_valleys(self, column: Optional[str] = None, distance: int = 1,
                               threshold: Optional[float] = None, *, result_column: str,
                               unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """ピーク (1) / バレー (-1) / その他 (0) のマーカー列を追加します

        Args:
            column: 対象列（省略時は荷重列）
            distance: 隣接ピーク間の最小距離
            threshold: ピークとみなす閾値
        """
        values = self._c.load_data if column is None else to_float_array(self._column_values(column))
        flags = compute_peaks_and_valleys(values, distance=distance, threshold=threshold)
        return self._with_column(result_column, flags, unit, ch, default_unit="")

    def to_hysteresis_table(self, *, cycle_column: Optional[str] = None) -> CoreOps[ColumnCollection]:
        """サイクルごとの履歴エネルギーと最大・最小荷重/変位を集計した表を返します

        戻り値のステップはサイクル番号、列は energy（単位は "荷重*変位"）/ max_load / min_load / max_disp / min_disp です。
        """
        load_unit, disp_unit = self._c.load.unit, self._c.displacement.unit
        rows = self.split_by_cycles(cycle_column=cycle_column).collect(
            lambda o: compute_hysteresis_energy(*o._ld_arrays()))
        units = {"energy": self._ld_unit("*"), "max_load": load_unit, "min_load": load_unit,
                 "max_disp": disp_unit, "min_disp": disp_unit}
        columns = {name: [row[i] for row in rows] for i, name in enumerate(units)}
        return CoreOps(ColumnCollection(columns, step=rows.keys, units=units, metadata=self._c.metadata))

    def to_stiffness_table(self, *, cycle_column: Optional[str] = None) -> CoreOps[ColumnCollection]:
        """サイクルごとの割線剛性を集計した表を返します（列: stiffness）"""
        unit = self._ld_unit("/")
        return self.split_by_cycles(cycle_column=cycle_column).collect(
            lambda o: ScalarResult("stiffness", compute_secant_stiffness(*o._ld_arrays()), unit=unit),
        ).to_table(name="stiffness")

    # ── 特殊曲線 ──────────────────────────────

    def to_skeleton_curve(self, *, cycle_column: Optional[str] = None, has_decrease: bool = False,
                          decrease_type: str = "envelope") -> Self:
        """スケルトン曲線を、荷重・変位の2列と "source_step" 列を持つ新しい荷重-変位コレクションとして返します

        変位列はサイクルごとにずらした値です。"source_step" は各点の元データのステップで、
        他の列は `select(steps=...)` で元データから取り出せます。
        cycle_column の省略時は、荷重の符号反転からサイクルを数えます（`mark_cycles` の既定と同じ）。

        Examples:
            >>> skel = cyclic.ops.to_skeleton_curve().end()
            >>> skel.columns
            ['荷重', '変位', 'source_step']
            >>> skel["source_step"].values
            array([ 1.,  2.,  3.,  4., 21., 22., 23., 24.])
            >>> len(cyclic.ops.select(steps=skel["source_step"].values.tolist()).end())
            8
        """
        return self._curve(*compute_skeleton_curve(*self._all_cycle_arrays(cycle_column), has_decrease=has_decrease,
                                                   decrease_type=decrease_type, return_index=True))

    def to_cumulative_curve(self, *, cycle_column: Optional[str] = None) -> Self:
        """累積塑性変形-荷重曲線を、`to_skeleton_curve` と同じ形の新しい荷重-変位コレクションとして返します

        荷重 0 まで延長した点は元データの行がないため、"source_step" は欠損になります。
        """
        return self._curve(*compute_cumulative_curve(*self._all_cycle_arrays(cycle_column), return_index=True))

    def _curve(self, displacement: np.ndarray, load: np.ndarray, rows: np.ndarray) -> Self:
        c = self._c
        steps = c.step
        values = {c.load_column: load, c.displacement_column: displacement}
        curve = LoadDisplacementCollection(
            {**{name: values[name] for name in c.columns if name in values},
             "source_step": [steps[i].item() if i >= 0 else None for i in rows]},
            load_column=c.load_column, displacement_column=c.displacement_column,
            meta={name: c[name].meta for name in values}, units={"source_step": ""}, metadata=c.metadata,
        )
        return self._next(curve)

    def _all_cycle_arrays(self, cycle_column: Optional[str]):
        return self._c.displacement_data, self._c.load_data, self._cycle_markers(cycle_column)
