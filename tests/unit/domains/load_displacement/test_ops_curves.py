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
    explicit = cyclic.ops.mark_cycles(result_column="load_cycle").to_skeleton_curve(cycle_column="load_cycle").end()
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


@pytest.mark.parametrize("method", ["to_skeleton_curve", "to_cumulative_curve"])
def test_curve_side_negative_matches_numeric(cyclic, method):
    func = compute_skeleton_curve if method == "to_skeleton_curve" else compute_cumulative_curve
    curve = getattr(cyclic.ops, method)(side="negative").end()
    d, p, rows = func(cyclic.displacement_data, cyclic.load_data, side="negative", return_index=True)
    assert isinstance(curve, LoadDisplacementCollection)
    np.testing.assert_allclose(curve.displacement_data, d)
    np.testing.assert_allclose(curve.load_data, p)
    expected_steps = [cyclic.step[i].item() if i >= 0 else None for i in rows]
    assert curve["source_step"].to_list() == expected_steps


@pytest.mark.parametrize("side", ["positive", "negative"])
def test_excursions_chained_equal_cumulative_curve(cyclic, side):
    parts = cyclic.ops.split_by_excursions(side=side)
    assert all(isinstance(c, LoadDisplacementCollection) for c in parts.end())
    joined = parts.chain("disp").concat().end()
    curve = cyclic.ops.to_cumulative_curve(side=side).end()
    np.testing.assert_allclose(joined.displacement_data, curve.displacement_data)
    np.testing.assert_allclose(joined.load_data, curve.load_data)
    np.testing.assert_array_equal(joined.step.astype(float), curve["source_step"].values)


def test_excursion_zero_rows_keep_other_columns_missing():
    col = ColumnCollection({"load": [0.0, 10.0, 20.0, 10.0, -10.0, -5.0, 15.0, 22.0],
                            "disp": [0.0, 1.0, 2.0, 1.5, 0.5, 0.0, 1.0, 2.5], "other": np.arange(8.0)},
                           step=list(range(1, 9)), units={"load": "kN", "disp": "mm"}, metadata={"specimen": "A"})
    ld = as_load_displacement(col, "load", "disp")
    first, second = ld.ops.split_by_excursions().end()
    np.testing.assert_array_equal(first.step.astype(float), [1, 2, 3, 4, np.nan])  # 終点の荷重 0 の点を補う
    np.testing.assert_array_equal(second.step.astype(float), [np.nan, 7, 8])       # 始点の荷重 0 の点を補う
    np.testing.assert_allclose(first.displacement_data[-1], 1.0)
    np.testing.assert_allclose(second.displacement_data[0], 0.25)
    assert first.load_data[-1] == 0.0 and np.isnan(first["other"].values[-1])
    assert first.columns == ld.columns and first["load"].unit == "kN" and first.metadata == ld.metadata
