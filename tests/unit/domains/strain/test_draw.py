import matplotlib.pyplot as plt

from tascpy.core.collection import ColumnCollection
from tascpy.domains import as_strain


def test_rosette_plot_without_ax_draws_on_new_figure(monkeypatch):
    from tascpy.domains.strain.draw import plot_rosette_vectors

    shown = []
    monkeypatch.setattr(plt, "show", lambda *a, **k: shown.append(True))
    ax = plot_rosette_vectors(0.0, 0.0, 1e-3, -5e-4, 30.0, "R1")
    assert shown == []
    assert len(ax.patches) == 4
    assert ax.get_title() == "Rosette: R1 (Step: 0)"
    plt.close(ax.figure)


def test_rosette_vectors_with_missing_value_use_nan():
    col = ColumnCollection({"a": [1.0, None], "b": [1.0, 2.0], "c": [1.0, 2.0]})
    strain = (col.ops.as_domain(as_strain, rosettes={"R": {"columns": ["a", "b", "c"]}}, coordinates={"a": {"x": 0.0, "y": 0.0}})
              .calculate_rosette_strains("R").end())
    ax = strain.plot.plot_rosette_vectors("R", step_index=1)
    assert ax is not None
