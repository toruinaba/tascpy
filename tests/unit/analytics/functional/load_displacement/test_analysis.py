import pytest
import numpy as np
from tascpy.analytics.functional.load_displacement.analysis import (
    compute_slopes,
    compute_stiffness,
    compute_yield_point_offset,
    compute_yield_point_general,
    compute_yield_point
)

def test_compute_slopes():
    disp = np.array([0.0, 1.0, 2.0, 2.5])
    load = np.array([0.0, 10.0, 30.0, 30.0])

    slopes = compute_slopes(disp, load)
    assert len(slopes) == 4
    assert np.isnan(slopes[0])
    assert np.isclose(slopes[1], 10.0) # (10-0)/(1-0)
    assert np.isclose(slopes[2], 20.0) # (30-10)/(2-1)
    assert np.isclose(slopes[3], 0.0)  # (30-30)/(2.5-2)

    with pytest.raises(ValueError):
        compute_slopes(np.array([1, 2]), np.array([1, 2, 3]))

    with pytest.raises(ValueError):
        compute_slopes(np.array([1]), np.array([1]))

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

def test_compute_yield_point_offset():
    # simulate load-disp
    disp = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    load = np.array([0.0, 100.0, 200.0, 250.0, 280.0, 290.0])
    
    initial_slope = 100.0
    
    is_valid, x, y, debug = compute_yield_point_offset(disp, load, initial_slope, offset_value=0.5)
    
    assert is_valid
    assert not np.isnan(x)
    assert not np.isnan(y)

def test_compute_yield_point_general():
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
    
    is_valid, x, y, debug = compute_yield_point_general(disp, load, initial_slope, factor=0.33)
    assert is_valid
    assert not np.isnan(x)

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

    # Fail silently
    is_valid, x, y, dbg = compute_yield_point(disp, load, method="unknown", fail_silently=True, range_start=0.1, range_end=0.8)
    assert not is_valid
    assert np.isnan(x)


def test_stiffness_and_yield_are_symmetric_for_compression():
    from tascpy.analytics.functional.load_displacement.analysis import compute_stiffness, compute_yield_point
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
    from tascpy.analytics.functional.load_displacement.analysis import compute_stiffness
    disp = np.array([0.0, 1.0, 2.0, 0.0, -1.0, -2.0, -3.0, -4.0])
    load = np.array([0.0, 10.0, 20.0, 0.0, -50.0, -100.0, -150.0, -200.0])
    assert np.isclose(compute_stiffness(disp, load, range_start=0.2, range_end=0.8), 50.0)
