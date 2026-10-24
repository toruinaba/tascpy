"""import 時に読み込まれるライブラリの検査（新しいインタプリタで実行する）"""

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"


def _run(code: str) -> None:
    env = {**os.environ, "PYTHONPATH": str(SRC), "MPLBACKEND": "Agg"}
    result = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("module", ["tascpy", "tascpy.numeric.curve", "tascpy.numeric.hysteresis",
                                    "tascpy.numeric.rosette", "tascpy.numeric.spatial"])
def test_numeric_does_not_load_polars_or_matplotlib(module):
    _run(f"""
        import sys
        import {module}
        loaded = {{"polars", "matplotlib", "tascpy.core"}} & set(sys.modules)
        assert not loaded, loaded
    """)


def test_model_does_not_load_matplotlib_until_plot():
    _run("""
        import sys
        import tascpy
        col = tascpy.ColumnCollection({"A": [1.0, 2.0]})
        col.ops.add("A", 1.0).end()
        tascpy.load, tascpy.LoadDisplacementCollection
        assert "matplotlib" not in sys.modules

        col.plot
        import matplotlib as mpl
        assert mpl.rcParams["font.family"] == ["IPAexGothic"]
    """)
