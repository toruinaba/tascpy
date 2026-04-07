import pytest
import numpy as np
from tascpy.analytics.functional.load_displacement.curves import (
    extend_data_edge,
    compute_skeleton_curve,
    compute_cumulative_curve
)

def test_extend_data_edge():
    x = [0.0, 1.0, 2.0]
    y = [0.0, 10.0, 20.0]

    # extend end to y=30
    x_new, y_new = extend_data_edge(x, y, 30.0, "y", "end")
    assert np.isclose(x_new, 3.0)
    assert np.isclose(y_new, 30.0)

    # extend end to x=3
    x_new, y_new = extend_data_edge(x, y, 3.0, "x", "end")
    assert np.isclose(x_new, 3.0)
    assert np.isclose(y_new, 30.0)

    # extend start to x=-1
    x_new, y_new = extend_data_edge(x, y, -1.0, "x", "start")
    assert np.isclose(x_new, -1.0)
    assert np.isclose(y_new, -10.0)

    # test short data
    x_short, y_short = extend_data_edge([1.0], [10.0], 20.0, "y", "end")
    assert x_short == 1.0
    assert y_short == 20.0

    # test flat lines
    x_flat, y_flat = extend_data_edge([0.0, 1.0], [10.0, 10.0], 2.0, "x", "end")
    assert np.isclose(x_flat, 2.0)
    assert np.isclose(y_flat, 10.0)


def test_compute_skeleton_curve():
    loads = np.array([0.0, 10.0, 5.0, 0.0, -10.0, 0.0, 15.0, 5.0, 0.0, -15.0, 0.0])
    disps = np.array([0.0, 1.0, 1.5, 2.0, 1.0, 0.0, 2.0, 2.5, 3.0, 1.5, 0.0])
    markers = np.array([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2])

    d_ske, p_ske = compute_skeleton_curve(loads, disps, markers, has_decrease=True, decrease_type="envelope")
    
    assert len(d_ske) > 0
    assert len(p_ske) > 0
    
    d_ske2, p_ske2 = compute_skeleton_curve(loads, disps, markers, has_decrease=True, decrease_type="continuous_only")
    assert len(d_ske2) > 0

    d_ske3, p_ske3 = compute_skeleton_curve(loads, disps, markers, has_decrease=True, decrease_type="both")
    assert len(d_ske3) > 0

    # Check invalid decrease type
    with pytest.raises(ValueError):
         compute_skeleton_curve(loads, disps, markers, has_decrease=True, decrease_type="invalid")

def test_compute_cumulative_curve():
    loads = np.array([0.0, 10.0, 0.0, -10.0, 0.0, 15.0, 0.0])
    disps = np.array([0.0, 1.0, 2.0, 1.0, 0.0, 2.0, 3.0])
    markers = np.array([1, 1, 1, 1, 1, 2, 2])
    
    d_cum, p_cum = compute_cumulative_curve(loads, disps, markers)
    assert len(d_cum) > 0
    assert len(p_cum) > 0
