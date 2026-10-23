import matplotlib as mpl
import matplotlib.pyplot as plt

from tascpy.visualization.config import JAPANESE_FONT, enable_japanese_font


def test_enable_japanese_font_only_sets_font_family_and_minus(monkeypatch):
    with mpl.rc_context():
        mpl.rcParams["font.size"] = 20
        assert enable_japanese_font()
        assert mpl.rcParams["font.family"] == [JAPANESE_FONT]
        assert mpl.rcParams["axes.unicode_minus"] is False
        assert mpl.rcParams["font.size"] == 20


def test_rosette_plot_without_ax_draws_on_new_figure(monkeypatch):
    from tascpy.visualization.functional.strain.plot import plot_rosette_vectors

    shown = []
    monkeypatch.setattr(plt, "show", lambda *a, **k: shown.append(True))
    ax = plot_rosette_vectors(0.0, 0.0, 1e-3, -5e-4, 30.0, "R1")
    assert shown == []
    assert len(ax.patches) == 4
    assert ax.get_title() == "Rosette: R1 (Step: 0)"
    plt.close(ax.figure)
