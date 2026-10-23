import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.core.result import PointResult, XYSeriesResult


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


@pytest.fixture
def ld():
    """解析結果を持つ荷重-変位コレクション（P [kN], d [mm]）"""
    col = ColumnCollection({"P": [0.0, 2.0, 4.0], "d": [0.0, 1.0, 2.0]}, units={"P": "kN", "d": "mm"})
    col = col.with_result(XYSeriesResult("skeleton_curve", Column("x", [1.0, 2.0]), Column("y", [2.0, 4.0])))
    col = col.with_result(XYSeriesResult("cumulative_curve", Column("x", [3.0, 4.0]), Column("y", [5.0, 6.0])))
    col = col.with_result(PointResult("yield_point", 1.5, 3.0, metadata={
        "method": "offset", "initial_slope": 2.0, "parameters": {"offset_value": 0.1, "range_start": 0.1, "range_end": 0.5},
    }))
    return col.ops.as_load_displacement("P", "d").end()


@pytest.fixture
def ld_without_results():
    return ColumnCollection({"P": [0.0, 1.0], "d": [0.0, 1.0]}).ops.as_load_displacement("P", "d").end()


def _line(ax, label):
    return next(line for line in ax.lines if line.get_label() == label)


def test_does_not_show(ld, monkeypatch):
    shown = []
    monkeypatch.setattr(plt, "show", lambda *a, **k: shown.append(True))
    ld.plot.plot_load_displacement()
    ld.plot.plot_skeleton_curve()
    ld.plot.plot_yield_analysis_details()
    assert shown == []


def test_labels_use_units_even_without_original(ld):
    ax = ld.plot.plot_skeleton_curve(plot_original=False)
    assert (ax.get_xlabel(), ax.get_ylabel()) == ("d [mm]", "P [kN]")
    assert [line.get_label() for line in ax.lines] == ["Skeleton Curve"]


def test_skeleton_and_cumulative_from_results(ld):
    ax = ld.plot.plot_skeleton_curve()
    np.testing.assert_array_equal(_line(ax, "Skeleton Curve").get_xdata(), [1.0, 2.0])
    np.testing.assert_array_equal(_line(ax, "Original Data").get_ydata(), [0.0, 2.0, 4.0])
    ax = ld.plot.plot_cumulative_curve()
    np.testing.assert_array_equal(_line(ax, "Cumulative Curve").get_ydata(), [5.0, 6.0])


@pytest.mark.parametrize("method", ["plot_skeleton_curve", "plot_cumulative_curve", "plot_yield_point",
                                    "plot_yield_analysis_details"])
def test_missing_results_raise(ld_without_results, method):
    with pytest.raises(ValueError):
        getattr(ld_without_results.plot, method)()


def test_yield_point_from_results(ld):
    ax = ld.plot.plot_yield_point()
    point = next(c for c in ax.collections if c.get_label() == "Yield Point (offset)")
    np.testing.assert_array_equal(point.get_offsets()[0], [1.5, 3.0])
    assert "Offset Line" in [line.get_label() for line in ax.lines]


def test_yield_point_explicit_values_win(ld):
    ax = ld.plot.plot_yield_point(yield_disp=0.5, yield_load=1.0, yield_method="general",
                                  yield_parameters={"factor": 0.5})
    point = next(c for c in ax.collections if c.get_label() == "Yield Point (general)")
    np.testing.assert_array_equal(point.get_offsets()[0], [0.5, 1.0])


def test_yield_details_show_units_and_range(ld):
    ax = ld.plot.plot_yield_analysis_details()
    text = ax.texts[0].get_text()
    assert "1.5000 mm" in text and "3.0000 kN" in text and "2.0000 kN/mm" in text
    assert any(c.get_label().startswith("Initial Slope Range") for c in ax.collections)


def test_yield_details_range_ignores_missing_loads():
    col = ColumnCollection({"P": [0.0, 1.0, None, 4.0, 5.0], "d": [0.0, 1.0, 2.0, 3.0, 4.0]})
    col = col.with_result(PointResult("yield_point", 3.0, 4.0, metadata={
        "method": "offset", "initial_slope": 1.0, "parameters": {"range_start": 0.1, "range_end": 0.9}}))
    ax = col.ops.as_load_displacement("P", "d").end().plot.plot_yield_analysis_details()
    highlighted = next(c for c in ax.collections if c.get_label().startswith("Initial Slope Range"))
    np.testing.assert_array_equal(highlighted.get_offsets()[:, 1], [1.0, 4.0])


def test_compare_yield_methods_warns_on_failure(ld_without_results):
    with pytest.warns(UserWarning, match="降伏点を求められませんでした"):
        ax = ld_without_results.plot.compare_yield_methods(methods=[{"method": "offset"}])
    assert ax.get_title() == "Comparison of Yield Point Methods"


def test_plot_multiple_curves(ld):
    curves = [
        {"x": np.array([1.0]), "y": np.array([2.0]), "kwargs": {"label": "explicit"}},
        {"type": "original", "kwargs": {"label": "original"}},
        {"type": "skeleton", "kwargs": {"label": "skeleton"}},
        {"type": "unknown"},
    ]
    with pytest.warns(UserWarning, match="未知の曲線"):
        ax = ld.plot.plot_multiple_curves(curves)
    assert [line.get_label() for line in ax.lines] == ["explicit", "original", "skeleton"]
    assert ax.get_xlabel() == "d [mm]"


def test_title_kwarg_is_not_duplicated(ld):
    ax = ld.plot.plot_yield_point(title="Custom")
    assert ax.get_title() == "Custom"


def test_original_curve_supports_scatter(ld):
    ax = ld.plot.plot_multiple_curves([{"type": "original", "kwargs": {"plot_type": "scatter", "s": 20}}])
    assert len(ax.collections) == 1


def test_peak_ignores_rows_with_missing_displacement():
    col = ColumnCollection({"P": [0.0, 2.0, 5.0, -100.0], "d": [0.0, 1.0, 2.0, None]})
    col = col.with_result(PointResult("yield_point", 1.5, 3.0, metadata={
        "method": "offset", "initial_slope": 2.0, "parameters": {"offset_value": 0.5, "range_start": 0.3, "range_end": 1.0}}))
    ax = col.ops.as_load_displacement("P", "d").end().plot.plot_yield_analysis_details()
    offset = next(line for line in ax.lines if line.get_label() == "Offset Line")
    assert offset._xy1[0] == 0.5  # 正側へずらす（変位が欠損した -100 kN の行は使わない）
    highlighted = next(c for c in ax.collections if c.get_label().startswith("Initial Slope Range"))
    np.testing.assert_array_equal(highlighted.get_offsets()[:, 1], [2.0, 5.0])


def test_compare_yield_methods_empty_list_runs_nothing(ld, monkeypatch):
    calls = []
    ops_type = type(ld.ops)
    original = ops_type.find_yield_point
    monkeypatch.setattr(ops_type, "find_yield_point", lambda self, **k: (calls.append(k), original(self, **k))[1])
    ld.plot.compare_yield_methods(methods=[])
    assert calls == []


def test_rosette_vectors_with_missing_value_use_nan():
    col = ColumnCollection({"a": [1.0, None], "b": [1.0, 2.0], "c": [1.0, 2.0]})
    strain = (col.ops.as_strain({"R": {"columns": ["a", "b", "c"]}}, {"a": {"x": 0.0, "y": 0.0}})
              .calculate_rosette_strains("R").end())
    ax = strain.plot.plot_rosette_vectors("R", step_index=1)
    assert ax is not None
