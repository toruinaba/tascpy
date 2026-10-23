import numpy as np
import polars as pl
import pytest

from tascpy.core.column import KEEP, Column, ColumnMeta, to_series


class TestToSeries:
    def test_numbers_become_float64_with_null(self):
        s = to_series("a", [1, None, 3])
        assert s.dtype == pl.Float64
        assert s.to_list() == [1.0, None, 3.0]

    def test_nan_becomes_null(self):
        assert to_series("a", np.array([1.0, np.nan])).null_count() == 1
        assert to_series("a", [1.0, float("nan")]).null_count() == 1

    def test_int_array_becomes_float(self):
        assert to_series("a", np.arange(3)).dtype == pl.Float64

    def test_all_missing_is_numeric(self):
        assert to_series("a", [None, None]).dtype == pl.Float64

    def test_strings_and_bools_keep_dtype(self):
        assert to_series("a", ["x", None]).dtype == pl.String
        assert to_series("a", [True, None]).dtype == pl.Boolean

    def test_mixed_numbers_and_strings_become_strings(self):
        s = to_series("a", [1.0, "x", None])
        assert s.dtype == pl.String
        assert s.to_list() == ["1.0", "x", None]

    def test_renames_series(self):
        assert to_series("b", pl.Series("a", [1.0])).name == "b"


class TestColumnMeta:
    def test_updated_keeps_unspecified(self):
        meta = ColumnMeta(unit="kN", ch="CH1")
        assert meta.updated(unit="N") == ColumnMeta(unit="N", ch="CH1")
        assert meta.updated(unit=KEEP) == meta

    def test_updated_can_clear_to_none(self):
        assert ColumnMeta(unit="kN").updated(unit=None).unit is None

    def test_is_frozen(self):
        with pytest.raises(AttributeError):
            ColumnMeta().unit = "x"  # type: ignore[misc]


class TestColumn:
    def test_values_numeric_nan(self):
        col = Column("load", [1.0, None, 3.0], unit="kN", ch="CH1")
        np.testing.assert_array_equal(col.values, [1.0, np.nan, 3.0])
        assert col.values.dtype == np.float64
        assert (col.name, col.unit, col.ch) == ("load", "kN", "CH1")

    def test_values_object_none(self):
        col = Column("s", ["a", None])
        assert list(col.values) == ["a", None]

    def test_values_are_read_only(self):
        col = Column("a", [1.0, 2.0])
        with pytest.raises(ValueError):
            col.values[0] = 9.0

    def test_scalar_access(self):
        col = Column("a", [1.0, None])
        assert col[0] == 1.0
        assert col[1] is None
        assert col.to_list() == [1.0, None]
        assert list(col) == [1.0, None]

    def test_stats_ignore_missing(self):
        col = Column("a", [1.0, None, 3.0, -4.0])
        assert col.max() == 3.0
        assert col.min() == -4.0
        assert col.mean() == 0.0
        assert col.sum() == 0.0
        assert col.median() == 1.0
        assert col.ptp() == 7.0
        assert col.abs_max() == 4.0
        assert col.quantile(0.5) == 1.0
        assert col.std() == pytest.approx(np.std([1.0, 3.0, -4.0], ddof=1))

    def test_stats_all_missing(self):
        col = Column("a", [None, None])
        assert col.max() is None
        assert col.mean() is None
        assert col.ptp() is None

    def test_numeric_stats_on_strings_are_none(self):
        col = Column("s", ["b", "a"])
        assert col.mean() is None
        assert col.max() == "b"

    def test_quantile_range(self):
        with pytest.raises(ValueError):
            Column("a", [1.0]).quantile(1.5)

    def test_missing_helpers(self):
        col = Column("a", [None, 1.0, None, 2.0])
        assert col.null_count() == 2
        assert col.n_valid == 2
        np.testing.assert_array_equal(col.is_valid(), [False, True, False, True])
        assert col.first_valid_index == 1
        assert col.first_invalid_index == 0

    def test_nearest_index(self):
        col = Column("a", [0.0, None, 10.0, 20.0])
        assert col.nearest_index(12.0) == 2
        assert Column("a", [None]).nearest_index(1.0) is None
        assert Column("s", ["x"]).nearest_index(1.0) is None

    def test_repr_shows_unit(self):
        assert "unit='kN'" in repr(Column("a", [1.0], unit="kN"))
