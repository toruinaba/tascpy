"""荷重-変位ドメインの曲線生成（skeleton_curve / cumulative_curve）のテスト"""

import numpy as np
import pytest

from tascpy.core.collection import ColumnCollection
from tascpy.domains import as_load_displacement
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.numeric.hysteresis import compute_cumulative_curve, compute_skeleton_curve

LOADS = [0, 10, 20, 10, 0, -10, -20, -10, 0, 15, 30, 15, 0, -15, -30]
DISPS = [0, 1, 2, 1, 0, -1, -2, -1, 0, 1.5, 3, 1.5, 0, -1.5, -3]
CYCLES = [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4]
STEPS = list(range(100, 115))


@pytest.fixture
def cyclic():
    col = ColumnCollection({"strain": np.arange(15.0), "load": LOADS, "disp": DISPS, "cycle": CYCLES},
                           step=STEPS, units={"load": "kN", "disp": "mm"}, metadata={"specimen": "A"})
    return as_load_displacement(col, "load", "disp").with_meta("load", ch="CH1")


@pytest.mark.parametrize("decrease_type", ["envelope", "continuous_only", "both"])
def test_skeleton_curve_matches_numeric(cyclic, decrease_type):
    curve = cyclic.ops.to_skeleton_curve(cycle_column="cycle", has_decrease=True, decrease_type=decrease_type).end()
    d, p, rows = compute_skeleton_curve(np.array(DISPS, float), np.array(LOADS, float), np.array(CYCLES),
                                        has_decrease=True, decrease_type=decrease_type, return_index=True)
    np.testing.assert_allclose(curve.displacement_data, d)
    np.testing.assert_allclose(curve.load_data, p)
    np.testing.assert_array_equal(curve["source_step"].values, np.array(STEPS)[rows])


def test_skeleton_curve_is_load_displacement_collection(cyclic):
    curve = cyclic.ops.to_skeleton_curve(cycle_column="cycle").end()
    assert isinstance(curve, LoadDisplacementCollection)
    assert curve.columns == ["load", "disp", "source_step"]
    assert (curve.load_column, curve.displacement_column) == ("load", "disp")
    assert (curve.load.unit, curve.displacement.unit, curve["source_step"].unit) == ("kN", "mm", "")
    assert curve.load.ch == "CH1"
    assert curve.metadata == {"specimen": "A"}
    np.testing.assert_array_equal(curve.step, np.arange(len(curve)))


def test_skeleton_curve_drops_results(cyclic):
    with_result = cyclic.with_result(cyclic.ops.stiffness())
    assert "stiffness" not in with_result.ops.to_skeleton_curve(cycle_column="cycle").end().results


def test_cycle_column_omitted_counts_load_sign_changes(cyclic):
    omitted = cyclic.ops.to_skeleton_curve().end()
    explicit = cyclic.ops.mark_cycles().to_skeleton_curve(cycle_column="load_cycle").end()
    np.testing.assert_allclose(omitted.load_data, explicit.load_data)
    np.testing.assert_allclose(omitted.displacement_data, explicit.displacement_data)
    assert "load_cycle" not in cyclic.ops.to_skeleton_curve().end().columns


def test_skeleton_curve_does_not_repeat_points(cyclic):
    curve = cyclic.ops.to_skeleton_curve(cycle_column="cycle", has_decrease=True, decrease_type="envelope").end()
    steps = curve["source_step"].values
    assert len(np.unique(steps)) == len(steps)


def test_skeleton_curve_chains_into_yield_point(cyclic):
    point = (cyclic.ops.to_skeleton_curve(cycle_column="cycle")
             .yield_point(range_start=0.1, range_end=0.5, fail_silently=True))
    assert (point.x_unit, point.y_unit) == ("mm", "kN")


def test_source_step_selects_original_rows(cyclic):
    curve = cyclic.ops.to_skeleton_curve(cycle_column="cycle").end()
    rows = cyclic.ops.select(steps=curve["source_step"].values.tolist()).end()
    np.testing.assert_allclose(rows.load_data, curve.load_data)
    assert "strain" in rows.columns


def test_cumulative_curve(cyclic):
    curve = cyclic.ops.to_cumulative_curve(cycle_column="cycle").end()
    d, p, rows = compute_cumulative_curve(np.array(DISPS, float), np.array(LOADS, float), np.array(CYCLES),
                                          return_index=True)
    assert curve.columns == ["load", "disp", "source_step"]
    np.testing.assert_allclose(curve.displacement_data, d)
    np.testing.assert_allclose(curve.load_data, p)
    source = curve["source_step"].values
    assert np.isnan(source[rows < 0]).all()
    np.testing.assert_array_equal(source[rows >= 0], np.array(STEPS)[rows[rows >= 0]])
