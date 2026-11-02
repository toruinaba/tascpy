"""CoreOps.row_where のテスト"""

import numpy as np
import pytest

from tascpy.core.collection import ColumnCollection
from tascpy.core.row import Row


@pytest.fixture
def col():
    # a は 0 → 20 → 0 と往復する（10 を 2 回横切る）。行 3 の b は欠損
    return ColumnCollection({"a": [0.0, 10.0, 20.0, 10.0, 0.0], "b": [1.0, 2.0, 3.0, None, 5.0],
                             "n": [0, 2, 4, 6, 8], "s": ["x", "y", "z", "w", "v"]},
                            step=[10, 20, 30, 40, 50], units={"a": "kN", "b": "mm"})


def test_interpolates_all_columns_and_step(col):
    row = col.ops.row_where("a", 5.0)
    assert isinstance(row, Row)
    assert row["a"] == 5.0 and row["b"] == 1.5 and row["n"] == 1.0
    assert row.step == 15.0 and row.unit("b") == "mm"
    assert row["s"] is None  # 数値でない列は None


def test_exact_value_is_that_row(col):
    row = col.ops.row_where("a", 20.0)
    assert row.step == 30 and row["b"] == 3.0
    assert row["s"] is None  # ちょうど行の位置でも、補間した行として扱う


def test_occurrence_selects_in_time_order(col):
    assert col.ops.row_where("a", 15.0).step == 25.0
    assert col.ops.row_where("a", 15.0, occurrence=1).step == 35.0
    assert col.ops.row_where("a", 15.0, occurrence=-1).step == 35.0


def test_missing_neighbor_gives_nan(col):
    row = col.ops.row_where("a", 15.0, occurrence=1)  # 行 2 と 3 の間。行 3 の b は欠損
    assert np.isnan(row["b"]) and row["a"] == 15.0


def test_missing_rows_in_search_column_are_skipped():
    c = ColumnCollection({"a": [0.0, None, 20.0], "b": [0.0, 1.0, 2.0]}, step=[1, 2, 3])
    row = c.ops.row_where("a", 5.0)  # 有効な行 0 と 2 の間で横切る（位置 0.5）
    assert row.step == 1.5 and row["b"] == 0.5


def test_no_crossing_raises_or_returns_empty_row(col):
    with pytest.raises(ValueError, match="位置がありません"):
        col.ops.row_where("a", 30.0)
    with pytest.raises(ValueError, match="位置がありません"):
        col.ops.row_where("a", 15.0, occurrence=2)
    row = col.ops.row_where("a", 30.0, fail_silently=True)
    assert np.isnan(row["a"]) and np.isnan(row.step) and row["s"] is None


def test_non_numeric_column_raises(col):
    with pytest.raises(TypeError):
        col.ops.row_where("s", 1.0)


def test_collect_to_table(col):
    parts = col.ops.split_by_integers([1, 1, 1, 2, 2])
    table = parts.collect(lambda o: o.row_where("b", 1.5, fail_silently=True)).to_table().end()
    assert table.step.tolist() == [1, 2]
    np.testing.assert_allclose(table["source_step"].values, [15.0, np.nan])
    assert table["b"].unit == "mm" and table["s"].to_list() == [None, None]
