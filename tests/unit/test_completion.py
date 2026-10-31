"""jedi の静的解析による補完の回帰テスト

marimo の補完は、まず jedi.Script でセルのコードを静的に解析し、候補がなければ実行済みの値で補完する。
後者ではプロパティ（`ops` / `plot`）を実行しないため、`col.ops.` などの補完は静的解析で型を追えるかで決まる。
"""

import pytest

jedi = pytest.importorskip("jedi")

PRELUDE = """import tascpy as tp
col = tp.ColumnCollection({"P": [0.0, 1.0], "d": [0.0, 1.0]})
"""


def _names(setup: str, expr: str) -> set:
    code = PRELUDE + setup + "\n" + expr
    return {c.name for c in jedi.Script(code).complete(code.count("\n") + 1, len(expr))}


@pytest.mark.parametrize("setup, expr, expected", [
    ("x = tp.as_load_displacement(col, load_column='P', displacement_column='d')", "x.", "load_column"),
    ("x = tp.as_load_displacement(col, load_column='P', displacement_column='d')", "x.ops.", "mark_cycles"),
    ("x = tp.as_coordinate(col)", "x.ops.", "interpolate_at_point"),
    ("x = tp.as_strain(col)", "x.ops.", "calculate_rosette_strains"),
    ("x = col.ops.abs('P', result_column='Q').end_as(tp.as_load_displacement, load_column='P', displacement_column='d')",
     "x.ops.", "mark_cycles"),
    ("", "col.ops.end_as(tp.as_strain).ops.", "calculate_rosette_strains"),
    ("parts = col.ops.split_by_integers([1, 2])", "parts[0].", "abs"),
    ("ld = tp.as_load_displacement(col, load_column='P', displacement_column='d')\n"
     "parts = ld.ops.split_by_cycles()", "parts[0].", "mark_cycles"),
    ("ld = tp.as_load_displacement(col, load_column='P', displacement_column='d')\n"
     "parts = ld.ops.split_by_cycles()", "parts[0].end().", "load_column"),
])
def test_static_completion(setup: str, expr: str, expected: str) -> None:
    assert expected in _names(setup, expr)
