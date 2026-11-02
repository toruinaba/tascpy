"""tascpy.numeric.position のテスト"""

import numpy as np
import pytest

from tascpy.numeric.position import find_crossings, interpolate_at, interpolate_positions


class TestInterpolateAt:
    def test_between_and_on_rows(self):
        assert interpolate_at([0.0, 10.0, 20.0], 0.25) == 2.5
        assert interpolate_at([0.0, 10.0, 20.0], 2.0) == 20.0

    def test_nan(self):
        assert np.isnan(interpolate_at([0.0, np.nan, 20.0], 0.5))
        assert np.isnan(interpolate_at([0.0, 10.0], np.nan))
        assert interpolate_at([0.0, np.nan], 0.0) == 0.0  # 整数の位置は隣の欠損に影響されない

    def test_out_of_range(self):
        with pytest.raises(ValueError, match="範囲外"):
            interpolate_at([0.0, 10.0], 1.5)
        with pytest.raises(ValueError, match="範囲外"):
            interpolate_at([0.0, 10.0], -0.5)

    def test_positions(self):
        np.testing.assert_array_equal(interpolate_positions([1, 2, 3], [0.5, np.nan]), [1.5, np.nan])
        assert interpolate_positions([1, 2], []).shape == (0,)


class TestFindCrossings:
    def test_crossings_in_time_order(self):
        np.testing.assert_array_equal(find_crossings([0.0, 10.0, 0.0, -10.0, 0.0], 5.0), [0.5, 1.5])

    def test_exact_rows_and_plateau(self):
        np.testing.assert_array_equal(find_crossings([0.0, 5.0, 10.0], 5.0), [1.0])
        np.testing.assert_array_equal(find_crossings([0.0, 5.0, 5.0, 0.0], 5.0), [1.0])  # 続く行は最初だけ
        np.testing.assert_array_equal(find_crossings([5.0, 0.0, 5.0], 5.0), [0.0, 2.0])

    def test_skips_nan(self):
        np.testing.assert_array_equal(find_crossings([0.0, np.nan, np.nan, 30.0], 10.0), [1.0])

    def test_none(self):
        assert find_crossings([0.0, 1.0], 5.0).shape == (0,)
        assert find_crossings([], 5.0).shape == (0,)
