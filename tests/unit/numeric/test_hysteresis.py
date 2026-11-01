import numpy as np
import pytest

from tascpy.numeric.hysteresis import (
    _extend_edge,
    chain_offsets,
    compute_bauschinger_curve,
    compute_cumulative_curve,
    compute_excursions,
    compute_cycle_markers,
    compute_hysteresis_energy,
    compute_load_clip,
    compute_plastic_deformation,
    compute_reversal_indices,
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
    np.testing.assert_allclose(p_ske[:3], [0.0, 10.0, 20.0])


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
    np.testing.assert_allclose(d_ske, [0.0, 1.0, 5.0 / 3.0])
    np.testing.assert_allclose(p_ske, [0.0, 10.0, 15.0])


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
    # 区間が1つなら、荷重 0 の点からの曲線そのもの（曲線が非線形でも）
    d_ske, p_ske = compute_skeleton_curve(np.array([0.0, 1.0, 2.0, 3.0, 4.0]), np.array([0.0, 10.0, 15.0, 17.0, 18.0]))
    np.testing.assert_allclose(d_ske, [0.0, 1.0, 2.0, 3.0, 4.0])
    np.testing.assert_allclose(p_ske, [0.0, 10.0, 15.0, 17.0, 18.0])


def test_skeleton_joins_where_load_equals_previous_max_row():
    # 2 つ目の区間は荷重 80（前の最大荷重）の行 (2, 80) から更新するので、その行を前の終点 (2, 80) に重ねる（ずらし量 0）
    disp = np.array([0.0, 1.0, 2.0, 1.0, 0.0, -1.0, -2.0, -1.0, 0.0, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 3.0, 0.0])
    load = np.array([0.0, 40.0, 80.0, 40.0, 0.0, -40.0, -80.0, -40.0, 0.0, 40.0, 80.0, 100.0, 102.0, 104.0, 106.0, 66.0, -54.0])
    d_ske, p_ske = compute_skeleton_curve(disp, load)
    np.testing.assert_allclose(d_ske, [0.0, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0])
    np.testing.assert_allclose(p_ske, [0.0, 40.0, 80.0, 100.0, 102.0, 104.0, 106.0])


def test_skeleton_joins_at_interpolated_point_of_previous_max():
    # 2 つ目の区間の (0, 0)-(3.5, 100) 上で荷重 80（前の最大荷重）になる点 x=2.8 を、前の終点 (2, 80) に重ねる
    disp = np.array([0.0, 1.0, 2.0, 1.0, -1.0, 0.0, 3.5, 4.5])
    load = np.array([0.0, 40.0, 80.0, 0.0, -20.0, 0.0, 100.0, 110.0])
    d_ske, p_ske, rows = compute_skeleton_curve(disp, load, return_index=True)
    np.testing.assert_allclose(d_ske, [0.0, 1.0, 2.0, 2.7, 3.7])
    np.testing.assert_allclose(p_ske, [0.0, 40.0, 80.0, 100.0, 110.0])
    np.testing.assert_array_equal(rows, [0, 1, 2, 6, 7])  # 補った点 (2.8 → 2.0) は前の終点と重なるので除く


@pytest.mark.parametrize("decrease_type", ["envelope", "continuous_only", "both"])
def test_skeleton_curve_return_index(decrease_type):
    d, p = compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED, has_decrease=True, decrease_type=decrease_type)
    d2, p2, rows = compute_skeleton_curve(CYCLIC_DISPS, CYCLIC_LOADS, ONE_BASED, has_decrease=True,
                                          decrease_type=decrease_type, return_index=True)
    assert_curves_equal((d2, p2), (d, p))
    real = rows >= 0
    np.testing.assert_allclose(CYCLIC_LOADS[rows[real]], p[real])
    assert len(np.unique(rows[real])) == real.sum()


def test_skeleton_curve_envelope_does_not_repeat_peak():
    # 最大荷重の行が変位も最大のとき、減少部分 (envelope) で同じ点を重ねない
    d, p = compute_skeleton_curve(np.array([0.0, 1.0, 0.0, -1.0, 0.0, 2.0, 0.0]),
                                  np.array([0.0, 10.0, 0.0, -10.0, 0.0, 15.0, 0.0]), has_decrease=True)
    np.testing.assert_allclose(p, [0.0, 10.0, 15.0])


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


class TestExcursions:
    def test_zero_crossing_is_interpolated_between_rows(self):
        # 正側の区間の終点は (1.5, 10) と (0.5, -10) の間、次の区間の始点は (0.0, -5) と (1.0, 15) の間
        disp = np.array([0.0, 1.0, 2.0, 1.5, 0.5, 0.0, 1.0, 2.5])
        load = np.array([0.0, 10.0, 20.0, 10.0, -10.0, -5.0, 15.0, 22.0])
        excursions = compute_excursions(disp, load)
        assert [e.rows.tolist() for e in excursions] == [[0, 1, 2, 3], [6, 7]]
        assert [(e.start, e.end) for e in excursions] == [(None, 1.0), (0.25, None)]
        d, p, rows = compute_cumulative_curve(disp, load, return_index=True)
        np.testing.assert_allclose(d, [0.0, 1.0, 2.0, 1.5, 1.0, 1.0, 1.75, 3.25])
        np.testing.assert_array_equal(rows, [0, 1, 2, 3, -1, -1, 6, 7])

    def test_negative_side_keeps_original_sign(self):
        disp = np.array([0.0, 1.0, 2.0, 1.5, 0.5, 0.0, 1.0, 2.5])
        load = np.array([0.0, 10.0, 20.0, 10.0, -10.0, -5.0, 15.0, 22.0])
        (e,) = compute_excursions(disp, load, side="negative")
        assert e.rows.tolist() == [4, 5] and (e.start, e.end) == (1.0, 0.25)

    def test_start_of_each_excursion_is_sum_of_previous_residuals(self):
        # 残留変形 1.0（0 → 1.0）と 1.0（2.0 → 3.0）の正側の区間が続く
        disp = np.array([0.0, 2.0, 1.0, 0.5, 2.0, 4.0, 3.0, 2.5, 3.0])
        load = np.array([0.0, 20.0, 0.0, -5.0, 0.0, 20.0, 0.0, -5.0, 0.0])
        assert [e.rows.tolist() for e in compute_excursions(disp, load)] == [[0, 1, 2], [4, 5, 6]]  # 荷重 0 だけの行 8 は区間にしない
        d, p, rows = compute_cumulative_curve(disp, load, return_index=True)
        np.testing.assert_allclose(d[np.isin(rows, [0, 2, 4, 6])], [0.0, 1.0, 1.0, 2.0])

    def test_zero_points_at_data_boundaries(self):
        # 先頭は荷重 0 から始まらず（最初の2行を延長して補う）、末尾は載荷途中で終わる（補わない）
        disp = np.array([0.2, 1.0, 2.0, 1.0, 0.0, 1.0, 2.0])
        load = np.array([8.0, 40.0, 80.0, 40.0, -10.0, 30.0, 60.0])
        excursions = compute_excursions(disp, load)
        assert excursions[0].start == pytest.approx(0.0) and excursions[-1].end is None
        d, p, rows = compute_cumulative_curve(disp, load, return_index=True)
        assert rows[0] == -1 and rows[-1] == 6
        np.testing.assert_allclose(d[:2], [0.0, 0.2])  # 延長した荷重 0 の点が 0 で、元の行の変位はずれない

    def test_exact_zero_rows_are_not_duplicated(self):
        disp = np.array([0.0, 1.0, 0.5, -0.5, -1.0, 0.0, 1.5])
        load = np.array([0.0, 10.0, 0.0, -10.0, -20.0, 0.0, 15.0])
        d, p, rows = compute_cumulative_curve(disp, load, return_index=True)
        assert -1 not in rows[:-1].tolist()
        np.testing.assert_allclose(d[:4], [0.0, 1.0, 0.5, 0.5])  # 2つ目の区間は荷重 0 の行 (0.0) を 0.5 に重ねる

    def test_missing_rows_are_skipped(self):
        disp = np.array([0.0, 1.0, np.nan, 0.0])
        load = np.array([0.0, 10.0, 5.0, 0.0])
        assert compute_excursions(disp, load)[0].rows.tolist() == [0, 1, 3]

    def test_chain_offsets(self):
        assert chain_offsets([0.5, 0.25, -1.0], [1.0, 2.5, 0.0]) == [-0.5, 0.25, 3.75]
        assert chain_offsets([], []) == []

    def test_unknown_side_raises(self):
        with pytest.raises(ValueError, match="side"):
            compute_excursions(CYCLIC_DISPS, CYCLIC_LOADS, side="both")


class TestComputeReversalIndices:
    def test_incremental_amplitude(self):
        d = np.array([0, 1, 0, -1, 0, 2, 0, -2, 0, 3])
        np.testing.assert_array_equal(compute_reversal_indices(d), [1, 3, 5, 7])

    def test_small_retreat_below_ratio_is_ignored(self):
        d = np.array([0, 1, 2, 1.95, 2.5, 0, -2])
        np.testing.assert_array_equal(compute_reversal_indices(d, ratio=0.05), [4])
        np.testing.assert_array_equal(compute_reversal_indices(d, ratio=0.0), [2, 3, 4])

    def test_ratio_scales_with_amplitude(self):
        # 振幅 10 で 0.4 戻っても 5% 未満、振幅 1 で 0.4 戻れば反転
        assert compute_reversal_indices(np.array([0, 10, 9.6, 12]), ratio=0.05).tolist() == []
        assert compute_reversal_indices(np.array([0, 1, 0.6]), ratio=0.05).tolist() == [1]

    def test_min_amplitude_suppresses_start_noise(self):
        d = np.array([0, 0.01, -0.01, 0.0, -1, 0, 1])
        assert compute_reversal_indices(d).tolist() == [1, 2, 3, 4]
        assert compute_reversal_indices(d, min_amplitude=0.1).tolist() == [4]

    def test_plateau_at_peak_uses_first_point(self):
        assert compute_reversal_indices(np.array([0, 2, 2, 2, 0])).tolist() == [1]

    def test_nan_is_skipped(self):
        d = np.array([np.nan, 0, 2, np.nan, 1, -1])
        assert compute_reversal_indices(d).tolist() == [2]

    def test_monotonic_and_empty(self):
        assert compute_reversal_indices(np.array([0, 1, 2, 3])).tolist() == []
        assert compute_reversal_indices(np.array([])).tolist() == []
        assert compute_reversal_indices(np.array([np.nan, np.nan])).tolist() == []

    @pytest.mark.parametrize("kwargs", [{"ratio": -0.1}, {"min_amplitude": -1.0}])
    def test_negative_parameters_raise(self, kwargs):
        with pytest.raises(ValueError):
            compute_reversal_indices(np.array([0, 1, 0]), **kwargs)


class TestPlasticDeformation:
    # 剛性 10・降伏荷重 10 の完全弾塑性: 荷重 -10 から +3 まで載荷（塑性変形 3）
    disp = np.array([-2.0, -1.0, 0.0, 1.0, 3.0])
    load = np.array([-10.0, 0.0, 10.0, 10.0, 10.0])
    kw = {"range_start": 0.0, "range_end": 0.6}

    def test_values(self):
        np.testing.assert_allclose(compute_plastic_deformation(self.disp, self.load, **self.kw), [0, 0, 0, 1, 3])

    def test_negative_loading(self):
        np.testing.assert_allclose(compute_plastic_deformation(-self.disp, -self.load, **self.kw), [0, 0, 0, 1, 3])

    @pytest.mark.parametrize("direction, last", [("positive", 3.0), ("negative", 0.0), ("both", 3.0)])
    def test_direction(self, direction, last):
        assert compute_plastic_deformation(self.disp, self.load, direction=direction, **self.kw)[-1] == pytest.approx(last)

    def test_monotonic_and_non_negative_with_noise(self):
        rng = np.random.default_rng(0)
        values = compute_plastic_deformation(self.disp, self.load + rng.normal(0, 0.3, 5), **self.kw)
        assert np.all(np.diff(values) >= 0) and values[0] == 0.0

    def test_elastic_is_zero(self):
        d = np.linspace(0.0, 2.0, 5)
        np.testing.assert_allclose(compute_plastic_deformation(d, 10 * d, **self.kw), 0.0, atol=1e-12)

    def test_missing_is_nan(self):
        d = self.disp.copy()
        d[3] = np.nan
        values = compute_plastic_deformation(d, self.load, **self.kw)
        assert np.isnan(values[3]) and values[-1] == pytest.approx(3.0)

    def test_offset_yield_point_has_offset_value(self):
        from tascpy.numeric.curve import compute_yield_point
        d, p = self.disp - self.disp[0], self.load - self.load[0]
        pt = compute_yield_point(d, p, offset_value=0.5, **self.kw)
        at = np.interp(pt.info["row_position"], np.arange(5), compute_plastic_deformation(d, p, **self.kw))
        assert at == pytest.approx(0.5)

    def test_stiffness_failure_raises(self):
        with pytest.raises(ValueError):
            compute_plastic_deformation(self.disp, self.load, range_start=0.0, range_end=0.2)

    def test_unknown_direction_raises(self):
        with pytest.raises(ValueError, match="direction"):
            compute_plastic_deformation(self.disp, self.load, direction="up")


class TestLoadClip:
    d = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    p = np.array([0.0, 10.0, 20.0, 30.0, 40.0])

    def test_lower_inserts_boundary(self):
        d, p, rows = compute_load_clip(self.d, self.p, lower=15.0)
        np.testing.assert_allclose(d, [1.5, 2.0, 3.0, 4.0])
        np.testing.assert_allclose(p, [15.0, 20.0, 30.0, 40.0])
        np.testing.assert_array_equal(rows, [-1, 2, 3, 4])

    def test_upper_and_both(self):
        d, p, rows = compute_load_clip(self.d, self.p, lower=5.0, upper=25.0)
        np.testing.assert_allclose(p, [5.0, 10.0, 20.0, 25.0])
        np.testing.assert_array_equal(rows, [-1, 1, 2, -1])

    def test_exact_boundary_row_is_not_duplicated(self):
        d, p, rows = compute_load_clip(self.d, self.p, lower=20.0)
        np.testing.assert_array_equal(rows, [2, 3, 4])

    def test_leaving_and_reentering(self):
        d, p, rows = compute_load_clip(np.arange(5.0), np.array([0.0, 20.0, 0.0, 20.0, 0.0]), lower=10.0)
        np.testing.assert_allclose(d, [0.5, 1.0, 1.5, 2.5, 3.0, 3.5])
        np.testing.assert_array_equal(rows, [-1, 1, -1, -1, 3, -1])

    def test_missing_points_are_skipped_and_empty(self):
        d, p, rows = compute_load_clip(np.array([0.0, np.nan, 2.0]), np.array([0.0, 10.0, 20.0]), lower=5.0)
        np.testing.assert_allclose(d, [0.5, 2.0])  # 欠損の点を飛ばして (0, 0)-(2, 20) で補間
        assert compute_load_clip(self.d, self.p, lower=100.0)[0].size == 0


class TestSkeletonAndBauschinger:
    # 0 → +1(10) → 0、0 → +2(20) → 0、0 → +1.5(15、弾性で戻る) → 0 の正側の区間（間に負側）
    disp = np.array([0.0, 1.0, 0.5, -0.5, 0.0, 1.0, 2.0, 1.5, 0.0, -0.5, 0.5, 1.5, 2.25, 1.75])
    load = np.array([0.0, 10.0, 0.0, -10.0, -5.0, 5.0, 20.0, 0.0, -10.0, -5.0, 5.0, 10.0, 15.0, 0.0])

    def test_skeleton_uses_only_updating_parts(self):
        d, p, rows = compute_skeleton_curve(self.disp, self.load, return_index=True)
        assert p.tolist() == [0.0, 10.0, 20.0]
        assert rows.tolist()[-1] == 6

    def test_bauschinger_is_the_rest_below_previous_max(self):
        d, p, rows = compute_bauschinger_curve(self.disp, self.load, return_index=True)
        assert np.all(p <= 20.0)
        assert 6 not in rows.tolist()           # 耐力の更新点は含まない
        assert 12 in rows.tolist()              # 更新しない区間（最大 15 < 20）はすべてバウシンガー部分
        assert d[0] == 0.0

    def test_first_excursion_has_no_bauschinger_part(self):
        d, p = compute_bauschinger_curve(np.array([0.0, 1.0, 2.0]), np.array([0.0, 10.0, 20.0]))
        assert d.size == 0

    @pytest.mark.parametrize("func", [compute_skeleton_curve, compute_bauschinger_curve])
    def test_negative_mirrors_positive(self, func):
        neg = func(self.disp, self.load, side="negative", return_index=True)
        mirrored = func(-self.disp, -self.load, return_index=True)
        np.testing.assert_allclose(neg[0], -mirrored[0])
        np.testing.assert_allclose(neg[1], -mirrored[1])
        np.testing.assert_array_equal(neg[2], mirrored[2])


class TestSkeletonDecrease:
    # 最大荷重 30 の区間のあと、耐力が低下する区間（荷重のピークのあと変位が伸びる）
    disp = np.array([0.0, 1.0, 2.0, 1.0, -1.0, 0.0, 3.0, 4.0, 5.0, 4.0, 2.0])
    load = np.array([0.0, 20.0, 30.0, 0.0, -20.0, 0.0, 25.0, 22.0, 18.0, 5.0, 0.0])

    def test_without_decrease_stops_at_max(self):
        d, p = compute_skeleton_curve(self.disp, self.load)
        assert p.max() == 30.0 and p[-1] == 30.0

    def test_envelope_adds_displacement_max_point(self):
        d, p, rows = compute_skeleton_curve(self.disp, self.load, has_decrease=True, decrease_type="envelope",
                                            return_index=True)
        assert rows.tolist()[-1] == 8 and p[-1] == 18.0

    def test_continuous_only_adds_branch_from_load_peak_to_displacement_peak(self):
        d, p, rows = compute_skeleton_curve(self.disp, self.load, has_decrease=True,
                                            decrease_type="continuous_only", return_index=True)
        assert rows.tolist()[-3:] == [6, 7, 8]

    def test_decrease_points_share_offset_of_max_excursion(self):
        # 最大荷重の区間（1 つ目）はずらし量 0 なので、減少部分の変位は元の値のまま
        d, p, rows = compute_skeleton_curve(self.disp, self.load, has_decrease=True, return_index=True)
        assert d[-1] == self.disp[8]


class TestBauschingerGap:
    # 1 つ目の区間の最大荷重 30。2 つ目の区間は 0 → 30 → 35（更新）→ 変位を伸ばしながら 20 まで低下
    disp = np.array([0.0, 1.0, 2.0, 1.0, -1.0, 0.0, 2.0, 3.0, 4.0, 5.0, 6.0, 5.0])
    load = np.array([0.0, 20.0, 30.0, 0.0, -20.0, 0.0, 20.0, 30.0, 35.0, 28.0, 20.0, 0.0])

    def test_part_above_previous_max_is_removed_without_gap(self):
        d, p, rows = compute_bauschinger_curve(self.disp, self.load, return_index=True)
        np.testing.assert_allclose(d, [0.0, 2.0, 3.0, 3.0 + 2 / 7, 3.0 + 2 / 7 + 1.0])
        np.testing.assert_allclose(p, [0.0, 20.0, 30.0, 28.0, 20.0])
        np.testing.assert_array_equal(rows, [5, 6, 7, 9, 10])  # 戻った境界の点は、出た点 (3.0, 30) と重なるので除く

    def test_clip_without_close_gaps_keeps_original_displacement(self):
        d, p, rows = compute_load_clip(self.disp[5:11], self.load[5:11], upper=30.0)
        np.testing.assert_allclose(d, [0.0, 2.0, 3.0, 4.0 + 5 / 7, 5.0, 6.0])

    def test_close_gaps_with_exact_boundary_rows(self):
        # 戻るときも荷重 30 の行を通る場合、その行を出た点に重ねて 1 つにする
        d, p, rows = compute_load_clip(np.array([0.0, 3.0, 4.0, 5.0, 6.0]), np.array([0.0, 30.0, 35.0, 30.0, 20.0]),
                                       upper=30.0, close_gaps=True)
        np.testing.assert_allclose(d, [0.0, 3.0, 4.0])
        np.testing.assert_array_equal(rows, [0, 1, 4])
