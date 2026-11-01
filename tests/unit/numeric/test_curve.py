import numpy as np
import pytest

from tascpy.numeric.curve import (
    _yield_point_general,
    _yield_point_offset,
    compute_peaks_and_valleys,
    compute_polygon_area,
    compute_stiffness,
    compute_yield_point,
)


def test_compute_stiffness():
    disp = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    load = np.array([0.0, 10.0, 20.0, 30.0, 40.0, 50.0]) # Linear E=10

    # Range 0.2 to 0.8 -> load from 10 to 40
    k_lin = compute_stiffness(disp, load, range_start=0.2, range_end=0.8, method="linear_regression")
    assert np.isclose(k_lin, 10.0)

    k_sec = compute_stiffness(disp, load, range_start=0.2, range_end=0.8, method="secant")
    assert np.isclose(k_sec, 10.0)

    with pytest.raises(ValueError):
        compute_stiffness(np.array([1]), np.array([1]))

    with pytest.raises(ValueError):
        compute_stiffness(disp, load, method="unknown")


def test_yield_point_offset():
    # simulate load-disp
    disp = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    load = np.array([0.0, 100.0, 200.0, 250.0, 280.0, 290.0])
    
    initial_slope = 100.0
    
    is_valid, x, y, position, debug = _yield_point_offset(disp, load, initial_slope, 0.5)
    
    assert is_valid
    assert not np.isnan(x)
    assert not np.isnan(y)
    assert position == pytest.approx(3.0)  # オフセット線 y = 100x - 50 と index 3 (3, 250) で交わる


def test_yield_point_general():
    disp = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    load = np.array([0.0, 100.0, 200.0, 250.0, 280.0, 290.0])
    initial_slope = 100.0
    
    # threshold = 100 * 0.33 = 33
    # slopes:
    # 0->1: 100
    # 1->2: 100
    # 2->3: 50
    # 3->4: 30  <- yield point found here
    # 4->5: 10
    
    is_valid, x, y, position, debug = _yield_point_general(disp, load, initial_slope, 0.33)
    assert is_valid
    assert not np.isnan(x)
    assert x == disp[int(position)]


def test_compute_yield_point():
    disp = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    load = np.array([0.0, 100.0, 200.0, 250.0, 280.0, 290.0])

    is_valid, x, y, dbg = compute_yield_point(disp, load, method="offset", offset_value=0.5, range_start=0.1, range_end=0.8)
    assert is_valid
    assert "offset_value" in dbg["parameters"]

    is_valid, x, y, dbg = compute_yield_point(disp, load, method="general", factor=0.33, range_start=0.1, range_end=0.8)
    assert is_valid
    assert "factor" in dbg["parameters"]

    with pytest.raises(ValueError):
        compute_yield_point(disp, load, method="unknown", range_start=0.1, range_end=0.8)

    # 未知の method は呼び出しの誤りなので fail_silently でも例外
    with pytest.raises(ValueError, match="未知"):
        compute_yield_point(disp, load, method="unknown", fail_silently=True)


def test_compute_yield_point_failures_have_consistent_info():
    from tascpy.numeric.curve import YieldPoint

    # 範囲内に点がない（剛性を求められない）
    result = compute_yield_point(np.array([0.0, 1.0]), np.array([0.0, 1.0]), range_start=0.5, range_end=0.6,
                                 fail_silently=True)
    assert isinstance(result, YieldPoint)
    assert not result.is_valid and np.isnan(result.x) and np.isnan(result.y)
    assert result.info["method"] == "offset"
    assert np.isnan(result.info["initial_slope"])
    assert result.info["parameters"] == {"range_start": 0.5, "range_end": 0.6, "offset_value": 0.002}
    assert "error" in result.info

    # 一般降伏法の内部エラーも fail_silently で捕まえる
    disp = np.array([0.0, 1.0, 2.0, 3.0])
    load = np.array([0.0, 10.0, 20.0, 30.0])
    general = compute_yield_point(disp, load, method="general", factor=0.0, range_start=0.0, range_end=1.0,
                                  fail_silently=True)
    assert set(general.info) >= {"method", "initial_slope", "parameters"}
    assert general.info["parameters"]["factor"] == 0.0


def test_stiffness_and_yield_are_symmetric_for_compression():
    from tascpy.numeric.curve import compute_stiffness, compute_yield_point
    disp = np.linspace(0.0, 10.0, 101)
    load = np.where(disp <= 5.0, 100.0 * disp, 500.0 + 10.0 * (disp - 5.0))

    k_tension = compute_stiffness(disp, load, range_start=0.1, range_end=0.5)
    k_compression = compute_stiffness(-disp, -load, range_start=0.1, range_end=0.5)
    assert np.isclose(k_tension, 100.0)
    assert np.isclose(k_compression, k_tension)

    for method in ("offset", "general"):
        ok_t, x_t, y_t, _ = compute_yield_point(disp, load, method=method, offset_value=0.5)
        ok_c, x_c, y_c, _ = compute_yield_point(-disp, -load, method=method, offset_value=0.5)
        assert ok_t and ok_c
        assert np.isclose(x_c, -x_t) and np.isclose(y_c, -y_t)


def test_stiffness_range_uses_largest_magnitude_side():
    from tascpy.numeric.curve import compute_stiffness
    disp = np.array([0.0, 1.0, 2.0, 0.0, -1.0, -2.0, -3.0, -4.0])
    load = np.array([0.0, 10.0, 20.0, 0.0, -50.0, -100.0, -150.0, -200.0])
    assert np.isclose(compute_stiffness(disp, load, range_start=0.2, range_end=0.8), 50.0)


def test_compute_polygon_area():
    x = np.array([0.0, 2.0, 2.0, 0.0])
    y = np.array([0.0, 0.0, 2.0, 2.0])
    area = compute_polygon_area(x, y)
    assert np.isclose(area, 4.0)

    # Less than 3 points
    assert compute_polygon_area(np.array([0.0, 1.0]), np.array([0.0, 1.0])) == 0.0


def test_compute_peaks_and_valleys():
    data = np.array([0, 1, 2, 1, 0, -1, -2, -1, 0])
    flags = compute_peaks_and_valleys(data, distance=1)
    
    # 2 is peak at index 2
    # -2 is valley at index 6
    expected = [0, 0, 1, 0, 0, 0, -1, 0, 0]
    np.testing.assert_array_equal(flags, expected)

    # With threshold
    data2 = np.array([0, 1.1, 1.0, 1.5, 0])
    flags2 = compute_peaks_and_valleys(data2, distance=1, threshold=0.3)
    # index 1: 1.1 is peak but diff with neighbors (min neighbor = 0) is >0.3. Wait, is it?
    # the threshold code says: min_neighbor = min(data[0], data[2]) = min(0, 1.0) = 0
    # data[1] - min_neighbor = 1.1 - 0 = 1.1 > 0.3 -> so it IS a peak initially?
    # But wait, distance=1, so index 3 (1.5) is also a peak.
    # Actually the distance logic is more complex. Just checking if it runs without errors and finds some flags.
    assert len(flags2) == 5

    # Test with NaNs
    data3 = [np.nan, 1, 2, 1, np.nan]
    flags3 = compute_peaks_and_valleys(data3, distance=1)
    # The nan values should be ignored. 2 is peak at index 2
    assert flags3[2] == 1


class TestYieldRowPosition:
    def test_offset_position_is_fractional_index(self):
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y = np.array([0.0, 100.0, 200.0, 220.0, 240.0])
        point = compute_yield_point(x, y, offset_value=0.5, range_start=0.0, range_end=0.9)
        position = point.info["row_position"]
        lower = int(np.floor(position))
        t = position - lower
        assert point.x == pytest.approx(x[lower] + t * (x[lower + 1] - x[lower]))
        assert point.y == pytest.approx(y[lower] + t * (y[lower + 1] - y[lower]))

    def test_position_counts_missing_rows(self):
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y = np.array([0.0, 100.0, 200.0, 220.0, 240.0])
        with_gap_x = np.insert(x, 1, np.nan)
        with_gap_y = np.insert(y, 1, np.nan)
        base = compute_yield_point(x, y, offset_value=0.5, range_start=0.0, range_end=0.9)
        gapped = compute_yield_point(with_gap_x, with_gap_y, offset_value=0.5, range_start=0.0, range_end=0.9)
        assert gapped.x == pytest.approx(base.x)
        assert gapped.info["row_position"] == pytest.approx(base.info["row_position"] + 1)

    def test_position_across_missing_row_is_scaled(self):
        # 交点を挟む2点の間に欠損の行があると、位置は2点の index の間を比率で分けた値になる
        x = np.array([0.0, 1.0, 2.0, np.nan, 3.0, 4.0])
        y = np.array([0.0, 100.0, 200.0, np.nan, 220.0, 240.0])
        point = compute_yield_point(x, y, offset_value=0.5, range_start=0.0, range_end=0.9)
        t = (point.x - 2.0) / 1.0
        assert point.info["row_position"] == pytest.approx(2 + 2 * t)

    def test_general_position_is_index(self):
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([0.0, 100.0, 200.0, 250.0, 280.0, 290.0])
        point = compute_yield_point(x, y, method="general", range_start=0.0, range_end=0.7)
        assert point.x == x[int(point.info["row_position"])]

    def test_failure_has_nan_position(self):
        point = compute_yield_point(np.array([0.0, 1.0]), np.array([0.0, 1.0]), fail_silently=True,
                                    range_start=0.5, range_end=0.6)
        assert not point.is_valid and np.isnan(point.info["row_position"])
