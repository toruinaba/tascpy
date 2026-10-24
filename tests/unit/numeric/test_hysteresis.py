import numpy as np
import pytest

from tascpy.numeric.hysteresis import (
    _extend_edge,
    compute_cumulative_curve,
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
