import numpy as np
import pytest

from tascpy.analytics.functional.coordinate.interpolation import interpolate

POINTS = np.array([[0.0, 0.0], [10.0, 0.0]])


def test_inverse_distance_midpoint_is_mean():
    assert float(interpolate(POINTS, [10.0, 20.0], [5.0, 0.0])) == pytest.approx(15.0)


@pytest.mark.parametrize("power", [1.0, 2.0, 3.0])
def test_inverse_distance_weights(power):
    w1, w2 = 1 / 2.5**power, 1 / 7.5**power
    expected = (10 * w1 + 20 * w2) / (w1 + w2)
    assert float(interpolate(POINTS, [10.0, 20.0], [2.5, 0.0], power=power)) == pytest.approx(expected)


def test_value_at_source_point():
    assert float(interpolate(POINTS, [10.0, 20.0], [10.0, 0.0])) == 20.0


def test_nearest():
    assert float(interpolate(POINTS, [10.0, 20.0], [2.0, 1.0], method="nearest")) == 10.0


def test_multiple_targets_and_time_series():
    values = np.array([[10.0, 0.0, 1.0], [20.0, 40.0, 1.0]])  # (N=2, T=3)
    result = interpolate(POINTS, values, [[5.0, 0.0], [0.0, 0.0]])
    assert result.shape == (2, 3)
    np.testing.assert_allclose(result, [[15.0, 20.0, 1.0], [10.0, 0.0, 1.0]])


def test_missing_values_are_ignored_per_column():
    values = np.array([[10.0, np.nan], [20.0, 40.0]])
    np.testing.assert_allclose(interpolate(POINTS, values, [5.0, 0.0]), [15.0, 40.0])
    # 補間先と一致する補間元が欠損なら、他の点から補間する
    np.testing.assert_allclose(interpolate(POINTS, values, [0.0, 0.0]), [10.0, 40.0])
    np.testing.assert_allclose(interpolate(POINTS, values, [1.0, 0.0], method="nearest"), [10.0, 40.0])


def test_all_missing_is_nan():
    values = np.array([[np.nan], [np.nan]])
    assert np.isnan(interpolate(POINTS, values, [1.0, 0.0])).all()
    assert np.isnan(interpolate(POINTS, values, [1.0, 0.0], method="nearest")).all()


def test_three_dimensional():
    points = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 10.0]])
    assert float(interpolate(points, [0.0, 100.0], [0.0, 0.0, 5.0])) == pytest.approx(50.0)


def test_errors():
    with pytest.raises(ValueError, match="次元"):
        interpolate(POINTS, [1.0, 2.0], [0.0, 0.0, 0.0])
    with pytest.raises(ValueError, match="inverse_distance"):
        interpolate(POINTS, [1.0, 2.0], [0.0, 0.0], method="linear")
