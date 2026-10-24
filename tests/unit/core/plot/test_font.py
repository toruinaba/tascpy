import matplotlib as mpl

from tascpy.core.plot.font import JAPANESE_FONT, enable_japanese_font


def test_enable_japanese_font_only_sets_font_family_and_minus(monkeypatch):
    with mpl.rc_context():
        mpl.rcParams["font.size"] = 20
        assert enable_japanese_font()
        assert mpl.rcParams["font.family"] == [JAPANESE_FONT]
        assert mpl.rcParams["axes.unicode_minus"] is False
        assert mpl.rcParams["font.size"] == 20
