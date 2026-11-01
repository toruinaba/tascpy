"""荷重-変位ドメインの操作"""

from __future__ import annotations

import warnings
from typing import Optional, Self, Tuple, TypeVar

import numpy as np
import polars as pl

from tascpy.core.collection import ColumnCollection
from tascpy.core.ops import CoreOps, to_float_array
from tascpy.core.ops_list import OpsList
from tascpy.core.result import PointResult, ScalarResult
from tascpy.numeric.curve import compute_peaks_and_valleys, compute_stiffness, compute_yield_point
from tascpy.numeric.hysteresis import (
    Direction,
    Side,
    compute_cumulative_curve,
    compute_cycle_markers,
    compute_excursions,
    compute_hysteresis_energy,
    compute_plastic_deformation,
    compute_reversal_indices,
    compute_secant_stiffness,
    compute_skeleton_curve,
)

from .collection import LoadDisplacementCollection

# OpsList[Self] は jedi（marimo の補完）が要素の型を解決できないため、self を TypeVar で受ける
LS = TypeVar("LS", bound="LoadDisplacementOps")


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

    def split_by_cycles(self: LS, *, cycle_column: Optional[str] = None) -> OpsList[LS]:
        """サイクル番号ごとに分割します（cycle_column の省略時は荷重の符号反転から数える）"""
        return self.split_by_integers(self._cycle_markers(cycle_column))

    def split_by_reversals(self: LS, *, column: Optional[str] = None, ratio: float = 0.05,
                           min_amplitude: float = 0.0) -> OpsList[LS]:
        """反転点（正側・負側の極値）から次の反転点までの半サイクルごとに分割します

        `split_by_cycles` が荷重の符号反転（0 をまたぐ位置）で切るのに対し、こちらはピークで切ります。
        除荷から逆方向の再載荷までが1つの区間に入るので、`shift_origin()` で区間の始点を原点にすれば、
        `yield_point` / `stiffness` で再降伏点や除荷剛性を半サイクルごとに求められます。

        隣り合う区間は境界の反転点を共有します（その点は両方の区間に入ります）。
        各要素のキー（`OpsList.keys`）は半サイクルの番号 1, 2, ... です。

        Args:
            column: 反転を見る列（省略時は変位列）
            ratio: 反転を確定する戻り量の、直前の反転点からの片振幅に対する比率
            min_amplitude: 反転とみなす最小の片振幅（column の単位。立ち上がりのノイズ除け）

        Examples:
            `cyclic` は 0 → +2 → -2 → +4 → 0 mm の載荷です。

            >>> parts = cyclic.ops.split_by_reversals()
            >>> parts.keys, [c["変位"].values[[0, -1]].tolist() for c in parts.end()]
            ([1, 2, 3, 4], [[0.0, 2.0], [2.0, -2.0], [-2.0, 4.0], [4.0, 0.0]])

            区間ごとに始点を原点へ移して降伏点を求めます。降伏点は移動後の座標なので、
            移動量（metadata の "origin_load"）を足すと元の荷重になります。
            弾性範囲で折り返した区間は降伏点が求まらず、欠損になります。

            >>> shifted = parts.map(lambda o: o.shift_origin())
            >>> points = shifted.collect(lambda o: o.yield_point(offset_value=0.5, range_start=0.1, range_end=0.5,
            ...                                                  fail_silently=True))
            >>> origin = shifted.collect(lambda o: o.end().metadata["origin_load"])
            >>> table = points.to_table(name="yield").join(origin.to_table(name="origin_load")).end()
            >>> (table["yield_y"].values + table["origin_load"].values).round(1)
            array([  nan,   nan, 102.2,   nan])
        """
        source = self._c.displacement_column if column is None else column
        values = to_float_array(self._column_values(source))
        reversals = compute_reversal_indices(values, ratio=ratio, min_amplitude=min_amplitude).tolist()
        bounds = [0, *reversals, len(self._c) - 1] if len(self._c) else []
        groups = [np.arange(a, b + 1) for a, b in zip(bounds[:-1], bounds[1:])]
        return self._split(groups, list(range(1, len(groups) + 1)))

    def split_by_excursions(self: LS, *, side: Side = "positive",
                            cycle_column: Optional[str] = None) -> OpsList[LS]:
        """荷重の片側の区間（荷重 0 の点から荷重 0 の点まで）ごとに分割します（荷重 0 基準）

        各区間は元データの行（全列・元のステップ）に、補間で求めた荷重 0 の点の行を前後に加えたものです。
        加えた行は、荷重が 0・変位が補間値（データの先頭では最初の2行の延長）で、ステップと他の列は欠損です
        （端の行の荷重がちょうど 0 の場合と、データの末尾で荷重 0 に届いていない端には加えません）。
        区間の取り方は `to_cumulative_curve` と同じです（`tascpy.numeric.hysteresis.compute_excursions`）。
        各要素のキーは区間の番号 1, 2, ... です。

        `OpsList.chain` で変位列をつなぐと累積曲線になり、`concat()` は `to_cumulative_curve` と同じ曲線です。

        Args:
            side: "positive"（荷重 >= 0 の区間）または "negative"（荷重 <= 0 の区間）
            cycle_column: サイクル番号の列（省略時は荷重の符号反転から数える。番号が変わる位置でも区切る）

        Examples:
            `cyclic` の正側の区間は、0 → +2 → 0 mm と、0 → +4 → 1.35 mm（荷重 0 の点）の2つです。

            >>> parts = cyclic.ops.split_by_excursions()
            >>> parts.keys, [c["変位"].values[[0, -1]].round(2).tolist() for c in parts.end()]
            ([1, 2], [[0.0, 0.0], [0.0, 1.35]])
            >>> bool(np.isnan(parts[1].end().step[-1]))  # 補った荷重 0 の点にはステップがない
            True

            区間をつなぐと累積曲線になります。

            >>> curve = parts.chain("変位").concat().end()
            >>> np.allclose(curve.displacement_data, cyclic.ops.to_cumulative_curve().end().displacement_data)
            True
        """
        excursions = compute_excursions(*self._all_cycle_arrays(cycle_column), side=side)
        parts = [self._next(self._with_zero_points(e.rows, e.start, e.end)) for e in excursions]
        return OpsList(parts, list(range(1, len(parts) + 1)))

    def _with_zero_points(self, rows: np.ndarray, start: Optional[float],
                          end: Optional[float]) -> LoadDisplacementCollection:
        """rows の行に、荷重 0 の点の行（ステップと他の列は欠損）を前後に加えたコレクション"""
        c = self._c
        part = c.take(rows)
        if start is None and end is None:
            return part

        def zero_row(x: float) -> pl.DataFrame:
            return pl.DataFrame({"step": pl.Series([None], dtype=part.df["step"].dtype),
                                 c.load_column: [0.0], c.displacement_column: [float(x)]})

        frames = ([] if start is None else [zero_row(start)]) + [part.df] + ([] if end is None else [zero_row(end)])
        return part._replace(df=pl.concat(frames, how="diagonal_relaxed").select(part.df.columns))

    def mark_plastic(self, *, range_start: float = 0.1, range_end: float = 0.3, direction: Direction = "both",
                     result_column: str, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """載荷区間の始点からの塑性変形を列として追加します（`split_by_reversals` の区間に使います）

        区間の最初の有効な点を原点とし、その曲線の剛性 K を range_start〜range_end の範囲から求めて
        （`shift_origin().yield_point()` の初期剛性と同じ求め方。範囲は `yield_point` とそろえます）、
        載荷の向きへの塑性変形 Δd − ΔP/K のそれまでの最大値（負なら 0）を求めます。値は始点で 0 で、単調に増えます。
        単位は省略時に変位列の単位です。剛性を求められない場合は、警告を出して 0 にします。

        区間ごとに求めた列を `OpsList.chain` でつなぐと、累積塑性変形になります。
        計算の詳細は `tascpy.numeric.hysteresis.compute_plastic_deformation` を参照してください。

        Args:
            range_start: 剛性を求める範囲の開始（ΔP の最大値に対する割合）
            range_end: 剛性を求める範囲の終了（ΔP の最大値に対する割合）
            direction: "both"、または "positive" / "negative"（載荷の向きが異なる区間は 0）

        Examples:
            `cyclic` は -2 → +4 mm の半サイクルで 1.35 mm 塑性化し、他の半サイクルは弾性です。

            >>> halves = cyclic.ops.split_by_reversals().map(
            ...     lambda o: o.mark_plastic(range_start=0.1, range_end=0.5, result_column="塑性"))
            >>> [round(float(c["塑性"].values[-1]), 2) for c in halves.end()]
            [0.0, 0.0, 1.35, 0.0]

            つなぐと累積塑性変形です。半サイクルの先頭の値が、その反転に入るまでの累積です。

            >>> cum = halves.chain("塑性")
            >>> [round(float(c["塑性"].values[0]), 2) for c in cum.end()]
            [0.0, 0.0, 0.0, 1.35]
        """
        c = self._c
        try:
            values = compute_plastic_deformation(c.displacement_data, c.load_data, range_start=range_start,
                                                 range_end=range_end, direction=direction)
        except ValueError as e:
            if "direction" in str(e):
                raise
            warnings.warn(f"塑性変形を 0 にしました（{e}）", UserWarning, stacklevel=2)
            values = np.where(c.valid_data_mask, 0.0, np.nan)
        return self._with_column(result_column, values, unit, ch, default_unit=c.displacement.unit)

    def until_peak(self, *, column: Optional[str] = None) -> Self:
        """先頭から、列の値が最初の有効な値から最も離れる行（ピーク）までの行を残します

        除荷を含む区間（`split_by_excursions` の区間など）から載荷部分を取り出し、`yield_point` / `stiffness` などの
        単調な曲線を前提にした計算に使うためのものです。ピークが複数の行にある場合は最初の行までです。

        Args:
            column: ピークを見る列（省略時は変位列）

        Raises:
            ValueError: 列に有効な値がない場合

        Examples:
            `cyclic` は 0 → +2 → -2 → ... mm の載荷なので、最初の正のピーク（+2 mm）ではなく、
            最も離れる +4 mm までを残します。

            >>> cyclic.ops.until_peak().end()["変位"].values[[0, -1]]
            array([0., 4.])

            区間ごとに使うと、各区間の載荷部分になります。

            >>> parts = cyclic.ops.split_by_excursions()
            >>> [c["変位"].values[[0, -1]].tolist() for c in parts.map(lambda o: o.until_peak()).end()]
            [[0.0, 2.0], [0.0, 4.0]]
        """
        name = self._c.displacement_column if column is None else column
        values = np.asarray(self._numeric(name), dtype=float)
        valid = np.flatnonzero(~np.isnan(values))
        if len(valid) == 0:
            raise ValueError(f"列 '{name}' に有効な値がありません")
        peak = int(np.nanargmax(np.abs(values - values[valid[0]])))
        return self._with_rows(np.arange(peak + 1))

    def shift_origin(self) -> Self:
        """最初の有効な点（荷重・変位とも欠損でない点）が原点になるよう、荷重と変位を平行移動します

        移動量は metadata の "origin_displacement" / "origin_load" に記録します（元の座標の値は
        移動後の値 + 移動量）。繰り返し呼ぶと移動量は累積します。
        `split_by_reversals` の区間に使うと、反転点を原点とした除荷・再載荷の曲線になります。

        Raises:
            ValueError: 荷重・変位とも欠損でない点がない場合

        Examples:
            >>> part = cyclic.ops.split_by_reversals()[2].shift_origin().end()
            >>> part["変位"].values[[0, -1]], part["荷重"].values[[0, -1]]
            (array([0., 6.]), array([  0., 186.]))
            >>> part["荷重"].unit
            'kN'
            >>> part.metadata["origin_displacement"], part.metadata["origin_load"]
            (-2.0, -80.0)
        """
        c = self._c
        d, p = c.displacement_data, c.load_data
        valid = np.flatnonzero(~(np.isnan(d) | np.isnan(p)))
        if len(valid) == 0:
            raise ValueError("荷重・変位とも欠損でない点がないため、原点を決められません")
        d0, p0 = float(d[valid[0]]), float(p[valid[0]])
        shifted = (c.with_column(c.displacement_column, d - d0).with_column(c.load_column, p - p0)
                   .with_metadata(origin_displacement=c.metadata.get("origin_displacement", 0.0) + d0,
                                  origin_load=c.metadata.get("origin_load", 0.0) + p0))
        return self._next(shifted)

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
                          decrease_type: str = "envelope", side: Side = "positive") -> Self:
        """スケルトン曲線を、荷重・変位の2列と "source_step" 列を持つ新しい荷重-変位コレクションとして返します

        変位列はサイクルごとにずらした値です。"source_step" は各点の元データのステップで、
        他の列は `select(steps=...)` で元データから取り出せます。
        cycle_column の省略時は、荷重の符号反転からサイクルを数えます（`mark_cycles` の既定と同じ）。
        side="negative" なら負側のスケルトン曲線（荷重・変位とも負の値）を返します。

        Examples:
            >>> skel = cyclic.ops.to_skeleton_curve().end()
            >>> skel.columns
            ['荷重', '変位', 'source_step']
            >>> skel["source_step"].values
            array([ 1.,  2.,  3.,  4., 21., 22., 23., 24.])
            >>> len(cyclic.ops.select(steps=skel["source_step"].values.tolist()).end())
            8
            >>> neg = cyclic.ops.to_skeleton_curve(side="negative").end()
            >>> neg["変位"].values, neg["荷重"].values
            (array([-0.5, -1. , -1.5, -2. ]), array([-20., -40., -60., -80.]))
        """
        return self._curve(*compute_skeleton_curve(*self._all_cycle_arrays(cycle_column), has_decrease=has_decrease,
                                                   decrease_type=decrease_type, side=side, return_index=True))

    def to_cumulative_curve(self, *, cycle_column: Optional[str] = None, side: Side = "positive") -> Self:
        """累積塑性変形-荷重曲線を、`to_skeleton_curve` と同じ形の新しい荷重-変位コレクションとして返します

        荷重 0 の点を補間で追加した点は元データの行がないため、"source_step" は欠損になります。
        区間ごとに扱いたいとき（区間ごとに降伏点を求めるなど）は `split_by_excursions(side=...).chain(変位列)` を使います。
        side="negative" なら負側の部分を負の向きにつないだ曲線を返します。
        """
        return self._curve(*compute_cumulative_curve(*self._all_cycle_arrays(cycle_column), side=side,
                                                     return_index=True))

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
