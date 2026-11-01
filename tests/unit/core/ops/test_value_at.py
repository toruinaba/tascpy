"""CoreOps.value_at のテスト"""

import numpy as np
import pytest

from tascpy.core.collection import ColumnCollection
from tascpy.core.result import PointResult
from tascpy.domains import as_load_displacement


@pytest.fixture
def col():
    return ColumnCollection({"a": [0.0, 10.0, 20.0, np.nan, 40.0], "s": ["x", "y", "z", "w", "v"]},
                            units={"a": "mm"})


def test_interpolates_between_rows(col):
    result = col.ops.value_at(1.25, "a")
    assert result.value == pytest.approx(12.5) and result.unit == "mm" and result.name == "a"


def test_integer_and_last_position(col):
    assert col.ops.value_at(2.0, "a").value == 20.0
    assert col.ops.value_at(4.0, "a").value == 40.0


def test_missing_neighbor_gives_nan(col):
    assert np.isnan(col.ops.value_at(2.5, "a").value)
    assert np.isnan(col.ops.value_at(float("nan"), "a").value)


def test_out_of_range_and_non_numeric_raise(col):
    with pytest.raises(ValueError, match="範囲外"):
        col.ops.value_at(4.5, "a")
    with pytest.raises(ValueError, match="範囲外"):
        col.ops.value_at(-0.1, "a")
    with pytest.raises(TypeError):
        col.ops.value_at(1.0, "s")


def test_point_result_uses_row_position(col):
    assert col.ops.value_at(PointResult("p", 0.0, 0.0, metadata={"row_position": 0.5}), "a").value == 5.0
    with pytest.raises(ValueError, match="row_position"):
        col.ops.value_at(PointResult("p", 0.0, 0.0), "a")


def test_yield_point_position_reproduces_point():
    # 降伏点の位置で荷重・変位列を読むと、降伏点そのものになる
    d = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    p = np.array([0.0, 100.0, 200.0, 230.0, 250.0, 260.0])
    ld = ColumnCollection({"P": p, "d": d}).ops.end_as(as_load_displacement, load_column="P", displacement_column="d")
    pt = ld.ops.yield_point(offset_value=0.5, range_start=0.0, range_end=0.7)
    assert ld.ops.value_at(pt, "d").value == pytest.approx(pt.x)
    assert ld.ops.value_at(pt, "P").value == pytest.approx(pt.y)
