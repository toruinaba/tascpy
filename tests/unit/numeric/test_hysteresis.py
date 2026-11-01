import numpy as np
import pytest

from tascpy.numeric.hysteresis import (
    _extend_edge,
    compute_cumulative_curve,
    compute_cumulative_positions,
    compute_cycle_markers,
    compute_hysteresis_energy,
    compute_secant_stiffness,
    compute_skeleton_curve,
)


def test_compute_cycle_markers():
    # Changes sign: + to - and - to +
    data = np.array([10.0, 5.0, -2.0, -8.0, 3.0, 1.0])
    markers = compute_cycle_markers(data, step=0.5)
    
    # 0 -> 10.0 (1.0)
    # 1 -> 5.0 (1.0)
    # 2 -> -2.0 (sign change -> 1.5)
    # 3 -> -8.0 (1.5)
    # 4 -> 3.0 (sign change -> 2.0)
    # 5 -> 1.0 (2.0)
    # Cast to int: [1, 1, 1, 1, 2, 2]
    # Wait, the step=0.5 means:
    # 1.0 -> 1.5 -> int=1. 1.5 -> 2.0 -> int=2
    np.testing.assert_array_equal(markers, [1, 1, 1, 1, 2, 2])
    
    # 欠損 (None/NaN) と 0 は飛ばし、直前の有効値と符号を比べる
    np.testing.assert_array_equal(compute_cycle_markers([10.0, None, -2.0], step=1.0), [1, 1, 2])


@pytest.mark.parametrize("data, expected", [
    ([10.0, 0.0, -10.0, 0.0, 10.0], [1, 1, 1, 1, 2]),
    ([10.0, np.nan, -10.0, np.nan, 10.0], [1, 1, 1, 1, 2]),
    ([10.0, 0.0, 0.0, 5.0, -5.0, 5.0], [1, 1, 1, 1, 1, 2]),  # 0 をはさんで同符号なら反転ではない
    ([0.0, 0.0, -5.0, 5.0, -5.0], [1, 1, 1, 1, 2]),           # 先頭の 0 は直前の有効値がない
    ([], []),
])
def test_compute_cycle_markers_skips_zero_and_missing(data, expected):
    np.testing.assert_array_equal(compute_cycle_markers(np.array(data), step=0.5), expected)


def test_compute_hysteresis_energy():
    loads = np.array([0.0, 10.0, 10.0, 0.0])
    disps = np.array([0.0, 0.0, 2.0, 2.0])
    
    energy, max_l, min_l, max_d, min_d = compute_hysteresis_energy(disps, loads)
    assert np.isclose(energy, 20.0)
    assert max_l == 10.0
    assert min_l == 0.0
    assert max_d == 2.0
    assert min_d == 0.0

    # Test mismatch length
    with pytest.raises(ValueError):
        compute_hysteresis_energy(np.array([1, 2]), np.array([1, 2, 3]))

    # Test less than 3 valid points
    e, ml, mnl, md, mnd = compute_hysteresis_energy(np.array([1, 2]), np.array([1, None]))
    assert e == 0.0
    assert np.isnan(ml)


def test_compute_secant_stiffness():
    # 最大荷重点 (1.0, 100) と最小荷重点 (-1.0, -100) を結ぶ: 200 / 2 = 100
    # 最大変位 (2.0) や最小変位 (-2.0) の点は使わない
    disps = np.array([0.0, 1.0, 2.0, 0.5, -1.0, -2.0, -0.5])
    loads = np.array([0.0, 100.0, 50.0, 0.0, -100.0, -50.0, 0.0])
    assert np.isclose(compute_secant_stiffness(disps, loads), 100.0)


def test_compute_secant_stiffness_ignores_missing_and_degenerate():
    assert np.isclose(compute_secant_stiffness(np.array([5.0, 1.0, -1.0, np.nan]),
                                               np.array([np.nan, 100.0, -100.0, 999.0])), 100.0)
    # 最大・最小荷重点の変位が同じなら NaN
    assert np.isnan(compute_secant_stiffness(np.array([1.0, 1.0]), np.array([0.0, 10.0])))
    assert np.isnan(compute_secant_stiffness(np.array([1.0]), np.array([1.0])))
    with pytest.raises(ValueError):
        compute_secant_stiffness(np.array([1.0, 2.0]), np.array([1.0]))


def test_compute_skeleton_curve():
    loads = np.array([0.0, 10.0, 5.0, 0.0, -10.0, 0.0, 15.0, 5.0, 0.0, -15.0, 0.0])
    disps = np.array([0.0, 1.0, 1.5, 2.0, 1.0, 0.0, 2.0, 2.5, 3.0, 1.5, 0.0])
    markers = np.array([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2])

    d_ske, p_ske = compute_skeleton_curve(disps, loads, markers, has_decrease=True, decrease_type="envelope")
    
    assert len(d_ske) > 0
    assert len(p_ske) > 0
    
    d_ske2, p_ske2 = compute_skeleton_curve(disps, loads, markers, has_decrease=True, decrease_type="continuous_only")
    assert len(d_ske2) > 0

    d_ske3, p_ske3 = compute_skeleton_curve(disps, loads, markers, has_decrease=True, decrease_type="both")
    assert len(d_ske3) > 0

    # Check invalid decrease type
    with pytest.raises(ValueError):
         compute_skeleton_curve(disps, loads, markers, has_decrease=True, decrease_type="invalid")


def assert_curves_equal(actual, expected):
    for a, e in zip(actual, expected):
        np.testing.assert_allclose(a, e)


CYCLIC_LOADS = np.array([0.0, 10.0, 5.0, 0.0, -10.0, 0.0, 15.0, 5.0, 0.0, -15.0, 0.0, 20.0, 12.0, 0.0])


CYCLIC_DISPS = np.array([0.0, 1.0, 1.5, 2.0, 1.0, 0.0, 2.0, 2.5, 3.0, 1.5, 0.0, 3.0, 4.0, 4.5])


ONE_BASED = np.array([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3])


@pytest.mark.parametrize("markers", [
    ONE_BASED - 1,                      # 0 始まり
    ONE_BASED * 10,                     # 連番でない
    np.where(ONE_BASED == 2, 7, ONE_BASED * 3),  # 間が飛ぶ (3, 7, 9)
    ONE_BASED.astype(float),            # Float64 列から渡される場合
])
@pytest.mark.parametrize("decrease_type", ["envelope", "continuous_only", "both"])
def test_compute_skeleton_curve_independent_of_marker_numbering(markers, decrease_type):
    expected = compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED, has_decrease=True,
                                      decrease_type=decrease_type)
    actual = compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, markers, has_decrease=True,
                                    decrease_type=decrease_type)
    np.testing.assert_allclose(actual[0], expected[0])
    np.testing.assert_allclose(actual[1], expected[1])
    assert len(expected[0]) > 0


def test_compute_skeleton_curve_single_cycle_zero_based():
    d_ske, p_ske = compute_skeleton_curve(
        np.array([0.0, 1.0, 2.0, 3.0, 4.0]), np.array([0.0, 10.0, 20.0, 15.0, 0.0]),
        np.array([0, 0, 0, 0, 0]), has_decrease=True,
    )
    expected = compute_skeleton_curve(
        np.array([0.0, 1.0, 2.0, 3.0, 4.0]), np.array([0.0, 10.0, 20.0, 15.0, 0.0]),
        np.array([1, 1, 1, 1, 1]), has_decrease=True,
    )
    assert_curves_equal((d_ske, p_ske), expected)
    np.testing.assert_allclose(p_ske[:2], [10.0, 20.0])


def test_curves_ignore_rows_without_marker():
    markers = ONE_BASED.astype(float)
    markers_with_gap = markers.copy()
    loads = CYCLIC_LOADS.copy()
    disps = CYCLIC_DISPS.copy()
    loads = np.insert(loads, 3, 999.0)
    disps = np.insert(disps, 3, 999.0)
    markers_with_gap = np.insert(markers_with_gap, 3, np.nan)

    assert_curves_equal(compute_skeleton_curve(disps, loads, markers_with_gap, has_decrease=True),
                        compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, markers, has_decrease=True))
    assert_curves_equal(compute_cumulative_curve(disps, loads, markers_with_gap),
                        compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS, markers))


@pytest.mark.parametrize("markers", [ONE_BASED - 1, ONE_BASED * 10])
def test_compute_cumulative_curve_independent_of_marker_numbering(markers):
    assert_curves_equal(compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS, markers),
                        compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED))


def test_curves_without_any_marker():
    markers = np.full(len(CYCLIC_LOADS), np.nan)
    for curve in (compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, markers),
                  compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS, markers)):
        assert all(isinstance(a, np.ndarray) and a.size == 0 for a in curve)


def test_compute_cumulative_curve():
    loads = np.array([0.0, 10.0, 0.0, -10.0, 0.0, 15.0, 0.0])
    disps = np.array([0.0, 1.0, 2.0, 1.0, 0.0, 2.0, 3.0])
    markers = np.array([1, 1, 1, 1, 1, 2, 2])
    
    d_cum, p_cum = compute_cumulative_curve(disps, loads, markers)
    assert len(d_cum) > 0
    assert len(p_cum) > 0


def test_unknown_keyword_is_rejected():
    with pytest.raises(TypeError):
        compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED, decrease_typ="both")
    with pytest.raises(TypeError):
        compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED, extra=1)


@pytest.mark.parametrize("decrease_type", ["envelope", "continuous_only", "both"])
def test_markers_default_to_cycles_counted_from_load(decrease_type):
    markers = compute_cycle_markers(CYCLIC_LOADS)
    assert_curves_equal(compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, has_decrease=True, decrease_type=decrease_type),
                        compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, markers, has_decrease=True,
                                               decrease_type=decrease_type))
    assert_curves_equal(compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS),
                        compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS, markers))


def test_curves_return_displacement_then_load():
    d_ske, p_ske = compute_skeleton_curve(np.array([0.0, 1.0, 0.0, -1.0, 0.0, 2.0, 0.0]),
                                          np.array([0.0, 10.0, 0.0, -10.0, 0.0, 15.0, 0.0]))
    np.testing.assert_allclose(d_ske, [1.0, 2.0])
    np.testing.assert_allclose(p_ske, [10.0, 15.0])


def test_extend_edge():
    x = [0.0, 1.0, 2.0]
    y = [0.0, 10.0, 20.0]

    # extend end to y=30
    x_new, y_new = _extend_edge(x, y, 30.0, "y", "end")
    assert np.isclose(x_new, 3.0)
    assert np.isclose(y_new, 30.0)

    # extend end to x=3
    x_new, y_new = _extend_edge(x, y, 3.0, "x", "end")
    assert np.isclose(x_new, 3.0)
    assert np.isclose(y_new, 30.0)

    # extend start to x=-1
    x_new, y_new = _extend_edge(x, y, -1.0, "x", "start")
    assert np.isclose(x_new, -1.0)
    assert np.isclose(y_new, -10.0)

    # test short data
    x_short, y_short = _extend_edge([1.0], [10.0], 20.0, "y", "end")
    assert x_short == 1.0
    assert y_short == 20.0

    # test flat lines
    x_flat, y_flat = _extend_edge([0.0, 1.0], [10.0, 10.0], 2.0, "x", "end")
    assert np.isclose(x_flat, 2.0)
    assert np.isclose(y_flat, 10.0)


def test_skeleton_of_single_monotonic_cycle_is_the_curve_itself():
    # 1 サイクル目は前の包絡線がないのでずらさない（曲線が非線形でも）
    d_ske, p_ske = compute_skeleton_curve(np.array([0.0, 1.0, 2.0, 3.0, 4.0]), np.array([0.0, 10.0, 15.0, 17.0, 18.0]))
    np.testing.assert_allclose(d_ske, [1.0, 2.0, 3.0, 4.0])
    np.testing.assert_allclose(p_ske, [10.0, 15.0, 17.0, 18.0])


def test_skeleton_offset_is_fixed_once_per_cycle_even_when_zero():
    # 2 サイクル目は前の包絡線の延長上 (x=2.5) から始まるのでずらし量は 0。以降の点でも計算し直さない
    disp = np.array([0.0, 1.0, 2.0, 1.0, 0.0, -1.0, -2.0, -1.0, 0.0, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 3.0, 0.0])
    load = np.array([0.0, 40.0, 80.0, 40.0, 0.0, -40.0, -80.0, -40.0, 0.0, 40.0, 80.0, 100.0, 102.0, 104.0, 106.0, 66.0, -54.0])
    d_ske, p_ske = compute_skeleton_curve(disp, load)
    np.testing.assert_allclose(d_ske, [1.0, 2.0, 2.5, 3.0, 3.5, 4.0])
    np.testing.assert_allclose(p_ske, [40.0, 80.0, 100.0, 102.0, 104.0, 106.0])


def test_skeleton_shifts_later_cycle_to_continue_the_envelope():
    # 2 サイクル目の載荷は残留変形 1.0 から始まり、前の包絡線 (0,0)-(1,40)-(2,80) の延長 x=2.5 (y=100) につなぐ
    disp = np.array([0.0, 1.0, 2.0, 1.0, -1.0, 0.0, 3.5, 4.5])
    load = np.array([0.0, 40.0, 80.0, 0.0, -20.0, 0.0, 100.0, 110.0])
    d_ske, p_ske = compute_skeleton_curve(disp, load)
    np.testing.assert_allclose(d_ske, [1.0, 2.0, 2.5, 3.5])
    np.testing.assert_allclose(p_ske, [40.0, 80.0, 100.0, 110.0])


@pytest.mark.parametrize("decrease_type", ["envelope", "continuous_only", "both"])
def test_skeleton_curve_return_index(decrease_type):
    d, p = compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED, has_decrease=True, decrease_type=decrease_type)
    d2, p2, rows = compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED, has_decrease=True,
                                          decrease_type=decrease_type, return_index=True)
    assert_curves_equal((d2, p2), (d, p))
    np.testing.assert_allclose(CYCLIC_LOADS[rows], p)
    assert len(np.unique(rows)) == len(rows)


def test_skeleton_curve_envelope_does_not_repeat_peak():
    # 最大荷重の行が変位も最大のとき、減少部分 (envelope) で同じ点を重ねない
    d, p = compute_skeleton_curve(np.array([0.0, 1.0, 0.0, -1.0, 0.0, 2.0, 0.0]),
                                  np.array([0.0, 10.0, 0.0, -10.0, 0.0, 15.0, 0.0]), has_decrease=True)
    np.testing.assert_allclose(p, [10.0, 15.0])


def test_cumulative_curve_return_index():
    d, p, rows = compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED, return_index=True)
    assert_curves_equal((d, p), compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED))
    real = rows >= 0
    np.testing.assert_allclose(CYCLIC_LOADS[rows[real]], p[real])
    np.testing.assert_allclose(p[~real], 0.0)


class TestCurveSide:
    """side="negative" は符号を反転したデータの正側と鏡像になる"""

    disp = np.array([0.0, 1.0, 2.0, 1.5, -1.0, -3.0, -2.5, 1.0, 3.0, 2.0, -2.0, -4.0, -3.0])
    load = np.array([0.0, 40.0, 50.0, 30.0, -40.0, -55.0, -35.0, 40.0, 55.0, 15.0, -45.0, -60.0, -20.0])

    @pytest.mark.parametrize("kwargs", [{}, {"has_decrease": True}, {"has_decrease": True, "decrease_type": "both"}])
    def test_skeleton_negative_mirrors_positive(self, kwargs):
        neg = compute_skeleton_curve(self.disp, self.load, side="negative", return_index=True, **kwargs)
        mirrored = compute_skeleton_curve(-self.disp, -self.load, return_index=True, **kwargs)
        np.testing.assert_allclose(neg[0], -mirrored[0])
        np.testing.assert_allclose(neg[1], -mirrored[1])
        np.testing.assert_array_equal(neg[2], mirrored[2])
        assert np.all(neg[1] <= 0)

    def test_cumulative_negative_mirrors_positive(self):
        neg = compute_cumulative_curve(self.disp, self.load, side="negative", return_index=True)
        mirrored = compute_cumulative_curve(-self.disp, -self.load, return_index=True)
        np.testing.assert_allclose(neg[0], -mirrored[0])
        np.testing.assert_allclose(neg[1], -mirrored[1])
        np.testing.assert_array_equal(neg[2], mirrored[2])
        assert not np.signbit(neg[1][neg[1] == 0]).any()  # -0.0 にならない

    def test_positive_is_default(self):
        for func in (compute_skeleton_curve, compute_cumulative_curve):
            default, positive = func(self.disp, self.load), func(self.disp, self.load, side="positive")
            np.testing.assert_array_equal(default[0], positive[0])
            np.testing.assert_array_equal(default[1], positive[1])

    @pytest.mark.parametrize("func", [compute_skeleton_curve, compute_cumulative_curve])
    def test_unknown_side_raises(self, func):
        with pytest.raises(ValueError, match="side"):
            func(self.disp, self.load, side="both")


class TestCumulativePositions:
    def test_zero_crossing_is_interpolated_between_rows(self):
        # 正側の区間の終点は (1.5, 10) と (0.5, -10) の間、次の区間の始点は (0.0, -5) と (1.0, 15) の間
        disp = np.array([0.0, 1.0, 2.0, 1.5, 0.5, 0.0, 1.0, 2.5])
        load = np.array([0.0, 10.0, 20.0, 10.0, -10.0, -5.0, 15.0, 22.0])
        d, p, rows = compute_cumulative_curve(disp, load, return_index=True)
        np.testing.assert_allclose(d, [0.0, 1.0, 2.0, 1.5, 1.0, 1.0, 1.75, 3.25])
        np.testing.assert_array_equal(rows, [0, 1, 2, 3, -1, -1, 6, 7])
        np.testing.assert_allclose(compute_cumulative_positions(disp, load),
                                   [0.0, 1.0, 2.0, 1.5, np.nan, np.nan, 1.75, 3.25])

    def test_curve_rows_match_positions(self):
        for side in ("positive", "negative"):
            d, _, rows = compute_cumulative_curve(CYCLIC_DISPS, CYCLIC_LOADS, side=side, return_index=True)
            positions = compute_cumulative_positions(CYCLIC_DISPS, CYCLIC_LOADS, side=side)
            np.testing.assert_allclose(d[rows >= 0], positions[rows[rows >= 0]])
            on_side = np.flatnonzero(~np.isnan(positions))
            np.testing.assert_array_equal(np.unique(rows[rows >= 0]), on_side)

    def test_start_of_each_excursion_is_sum_of_previous_residuals(self):
        # 残留変形 1.0（0 → 1.0）と 1.0（2.0 → 3.0）の正側の区間が続く
        disp = np.array([0.0, 2.0, 1.0, 0.5, 2.0, 4.0, 3.0, 2.5, 3.0])
        load = np.array([0.0, 20.0, 0.0, -5.0, 0.0, 20.0, 0.0, -5.0, 0.0])
        positions = compute_cumulative_positions(disp, load)
        np.testing.assert_allclose(positions[[0, 2, 4, 6]], [0.0, 1.0, 1.0, 2.0])
        assert np.isnan(positions[8])  # 荷重 0 の行だけの範囲は区間にしない

    def test_no_zero_point_at_data_boundaries(self):
        # 先頭は荷重 0 から始まらず、末尾は載荷途中で終わる
        disp = np.array([0.1, 1.0, 2.0, 1.0, 0.0, 1.0, 2.0])
        load = np.array([4.0, 40.0, 80.0, 40.0, -10.0, 30.0, 60.0])
        d, p, rows = compute_cumulative_curve(disp, load, return_index=True)
        assert rows[0] == 0 and rows[-1] == 6  # 端に荷重 0 の点を追加しない
        np.testing.assert_allclose(d[0], 0.1)  # 先頭の区間は元の変位のまま

    def test_exact_zero_rows_are_not_duplicated(self):
        disp = np.array([0.0, 1.0, 0.5, -0.5, -1.0, 0.0, 1.5])
        load = np.array([0.0, 10.0, 0.0, -10.0, -20.0, 0.0, 15.0])
        d, p, rows = compute_cumulative_curve(disp, load, return_index=True)
        assert -1 not in rows[:-1].tolist()
        np.testing.assert_allclose(d[:4], [0.0, 1.0, 0.5, 0.5])  # 2つ目の区間は荷重 0 の行 (0.0) を 0.5 に重ねる

    def test_missing_rows_are_nan(self):
        disp = np.array([0.0, 1.0, np.nan, 0.0])
        load = np.array([0.0, 10.0, 5.0, 0.0])
        assert np.isnan(compute_cumulative_positions(disp, load)[2])

    def test_unknown_side_raises(self):
        with pytest.raises(ValueError, match="side"):
            compute_cumulative_positions(CYCLIC_DISPS, CYCLIC_LOADS, side="both")
