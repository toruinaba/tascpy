import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from tascpy.core.collection import ColumnCollection
from tascpy.core.result import PointResult
from tascpy.domains import as_load_displacement


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


@pytest.fixture
def ld():
    """荷重-変位コレクション（P [kN], d [mm]）"""
    col = ColumnCollection({"P": [0.0, 2.0, 4.0], "d": [0.0, 1.0, 2.0]}, units={"P": "kN", "d": "mm"})
    return col.ops.end_as(as_load_displacement, load_column="P", displacement_column="d")


@pytest.fixture
def point():
    return PointResult("yield_point", 1.5, 3.0, metadata={
        "method": "offset", "initial_slope": 2.0, "parameters": {"offset_value": 0.1, "range_start": 0.1, "range_end": 0.5},
    })


@pytest.fixture
def ld_short():
    col = ColumnCollection({"P": [0.0, 1.0], "d": [0.0, 1.0]})
    return col.ops.end_as(as_load_displacement, load_column="P", displacement_column="d")


def _line(ax, label):
    return next(line for line in ax.lines if line.get_label() == label)


def test_does_not_show(ld, point, monkeypatch):
    shown = []
    monkeypatch.setattr(plt, "show", lambda *a, **k: shown.append(True))
    ld.plot.plot_load_displacement()
    ld.plot.plot_yield_analysis_details(point)
    assert shown == []


def test_yield_point(ld, point):
    ax = ld.plot.plot_yield_point(point)
    marker = next(c for c in ax.collections if c.get_label() == "Yield Point (offset)")
    np.testing.assert_array_equal(marker.get_offsets()[0], [1.5, 3.0])
    assert "Offset Line" in [line.get_label() for line in ax.lines]


def test_yield_point_from_ops(ld):
    point = ld.ops.yield_point(method="general", range_start=0.1, range_end=0.9, fail_silently=True)
    ax = ld.plot.plot_yield_point(point)
    assert any(c.get_label() == "Yield Point (general)" for c in ax.collections)


def test_yield_details_show_units_and_range(ld, point):
    ax = ld.plot.plot_yield_analysis_details(point)
    text = ax.texts[0].get_text()
    assert "1.5000 mm" in text and "3.0000 kN" in text and "2.0000 kN/mm" in text
    assert any(c.get_label().startswith("Initial Slope Range") for c in ax.collections)


def test_yield_details_range_ignores_missing_loads():
    col = ColumnCollection({"P": [0.0, 1.0, None, 4.0, 5.0], "d": [0.0, 1.0, 2.0, 3.0, 4.0]})
    point = PointResult("yield_point", 3.0, 4.0, metadata={
        "method": "offset", "initial_slope": 1.0, "parameters": {"range_start": 0.1, "range_end": 0.9}})
    ld = col.ops.end_as(as_load_displacement, load_column="P", displacement_column="d")
    ax = ld.plot.plot_yield_analysis_details(point)
    highlighted = next(c for c in ax.collections if c.get_label().startswith("Initial Slope Range"))
    np.testing.assert_array_equal(highlighted.get_offsets()[:, 1], [1.0, 4.0])


def test_compare_yield_points_skips_invalid_points(ld, point):
    failed = PointResult("yield_point", float("nan"), float("nan"), metadata={"method": "general", "is_valid": False})
    with pytest.warns(UserWarning, match="求まらなかった降伏点"):
        ax = ld.plot.compare_yield_points([point, failed])
    assert ax.get_title() == "Comparison of Yield Point Methods"
    assert [c.get_label() for c in ax.collections] == ["Offset (0.1)"]


def test_compare_yield_points_does_not_run_analysis(ld, point, monkeypatch):
    monkeypatch.setattr(type(ld.ops), "yield_point", lambda self, **k: pytest.fail("plotter must not analyse"))
    ld.plot.compare_yield_points([point])


def test_plot_multiple_curves(ld):
    curves = [{"x": np.array([1.0]), "y": np.array([2.0]), "kwargs": {"label": "explicit"}}]
    ax = ld.plot.plot_multiple_curves(curves, plot_original=True, original_kwargs={"label": "original"})
    assert [line.get_label() for line in ax.lines] == ["original", "explicit"]
    assert ax.get_xlabel() == "d [mm]"
    assert [line.get_label() for line in ld.plot.plot_multiple_curves(curves).lines] == ["explicit"]
    with pytest.raises(ValueError, match="x / y がありません"):
        ld.plot.plot_multiple_curves([{"kwargs": {}}])


def test_title_kwarg_is_not_duplicated(ld, point):
    ax = ld.plot.plot_yield_point(point, title="Custom")
    assert ax.get_title() == "Custom"


def test_original_curve_supports_scatter(ld):
    ax = ld.plot.plot_multiple_curves([], plot_original=True, original_kwargs={"plot_type": "scatter", "s": 20})
    assert len(ax.collections) == 1


def test_peak_ignores_rows_with_missing_displacement():
    col = ColumnCollection({"P": [0.0, 2.0, 5.0, -100.0], "d": [0.0, 1.0, 2.0, None]})
    point = PointResult("yield_point", 1.5, 3.0, metadata={
        "method": "offset", "initial_slope": 2.0, "parameters": {"offset_value": 0.5, "range_start": 0.3, "range_end": 1.0}})
    ld = col.ops.end_as(as_load_displacement, load_column="P", displacement_column="d")
    ax = ld.plot.plot_yield_analysis_details(point)
    offset = next(line for line in ax.lines if line.get_label() == "Offset Line")
    assert offset._xy1[0] == 0.5  # 正側へずらす（変位が欠損した -100 kN の行は使わない）
    highlighted = next(c for c in ax.collections if c.get_label().startswith("Initial Slope Range"))
    np.testing.assert_array_equal(highlighted.get_offsets()[:, 1], [2.0, 5.0])
