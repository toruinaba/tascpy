import numpy as np
import polars as pl
import pytest

from tascpy.core import Column, ColumnCollection, ColumnMeta, PointResult, Row, concat


@pytest.fixture
def coll():
    return ColumnCollection(
        {"P": [0.0, 10.0, None, 30.0], "d": [0.0, 1.0, 2.0, 3.0], "s": ["a", "b", "b", "c"]},
        step=[1, 2, 3, 4],
        units={"P": "kN", "d": "mm"},
        metadata={"source": "test"},
    )


class TestConstruction:
    def test_columns_units_and_index(self, coll):
        assert coll.columns == ["P", "d", "s"]
        assert coll.units == {"P": "kN", "d": "mm", "s": None}
        np.testing.assert_array_equal(coll.step, [1, 2, 3, 4])
        assert coll.df.columns == ["step", "P", "d", "s"]
        assert coll.shape == (4, 3)
        assert len(coll) == 4

    def test_default_step(self):
        np.testing.assert_array_equal(ColumnCollection({"a": [5.0, 6.0]}).step, [0, 1])

    def test_empty(self):
        empty = ColumnCollection()
        assert len(empty) == 0
        assert empty.columns == []

    def test_column_objects_keep_meta(self):
        c = ColumnCollection({"a": Column("x", [1.0], unit="N", ch="CH1")})
        assert c.meta["a"] == ColumnMeta(unit="N", ch="CH1")
        assert c["a"].name == "a"

    def test_units_and_meta_override(self):
        c = ColumnCollection({"a": Column("a", [1.0], unit="N")}, units={"a": "kN"})
        assert c["a"].unit == "kN"
        c = ColumnCollection({"a": [1.0]}, meta={"a": ColumnMeta(ch="CH9")})
        assert c["a"].ch == "CH9"

    def test_unknown_unit_key(self):
        with pytest.raises(KeyError):
            ColumnCollection({"a": [1.0]}, units={"b": "N"})

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            ColumnCollection({"a": [1.0, 2.0], "b": [1.0]})
        with pytest.raises(ValueError):
            ColumnCollection({"a": [1.0, 2.0]}, step=[1])

    def test_reserved_names(self):
        with pytest.raises(ValueError):
            ColumnCollection({"step": [1.0]})

    def test_date_time_index(self):
        c = ColumnCollection({"a": [1.0, 2.0]}, date=["d1", "d2"], time=["t1", "t2"])
        assert c.columns == ["a"]
        assert list(c.date) == ["d1", "d2"]
        assert list(c.time) == ["t1", "t2"]
        assert ColumnCollection({"a": [1.0]}).date is None

    def test_from_frame(self):
        df = pl.DataFrame({"t": [0.1, 0.2], "a": [1, 2], "date": ["x", "y"]})
        c = ColumnCollection.from_frame(df, step="t", units={"a": "N"})
        np.testing.assert_array_equal(c.step, [0.1, 0.2])
        assert c.columns == ["a"]
        assert c.units == {"a": "N"}
        assert list(c.date) == ["x", "y"]

    def test_from_frame_uses_step_column(self):
        c = ColumnCollection.from_frame(pl.DataFrame({"step": [5, 6], "a": [1.0, 2.0]}))
        np.testing.assert_array_equal(c.step, [5, 6])

    def test_from_frame_rejects_ambiguous_step(self):
        with pytest.raises(ValueError):
            ColumnCollection.from_frame(pl.DataFrame({"step": [1], "t": [1]}), step="t")


class TestRead:
    def test_getitem_column(self, coll):
        col = coll["P"]
        assert isinstance(col, Column)
        assert col.unit == "kN"
        np.testing.assert_array_equal(col.values, [0.0, 10.0, np.nan, 30.0])

    def test_getitem_missing_and_index_names(self, coll):
        with pytest.raises(KeyError):
            coll["nope"]
        with pytest.raises(KeyError, match="coll.step"):
            coll["step"]

    def test_getitem_row(self, coll):
        row = coll[0]
        assert isinstance(row, Row)
        assert row.step == 1
        assert row["P"] == 0.0
        assert coll[-1]["s"] == "c"
        assert coll[2]["P"] is None
        with pytest.raises(IndexError):
            coll[4]

    def test_getitem_slice(self, coll):
        part = coll[1:3]
        np.testing.assert_array_equal(part.step, [2, 3])
        assert part.units == coll.units

    def test_getitem_type_error(self, coll):
        with pytest.raises(TypeError):
            coll[1.5]

    def test_contains_and_not_iterable(self, coll):
        assert "P" in coll
        assert "step" not in coll
        with pytest.raises(TypeError):
            iter(coll)

    def test_by_ch(self):
        c = ColumnCollection({"a": Column("a", [1.0], ch="CH1")})
        assert c.by_ch("CH1").name == "a"
        with pytest.raises(KeyError):
            c.by_ch("CH2")

    def test_iter_rows(self, coll):
        assert [r.step for r in coll.iter_rows()] == [1, 2, 3, 4]

    def test_step_index(self, coll):
        assert coll.step_index(3) == 2
        assert coll.step_index(99) is None
        assert coll.step_index(2.9, tolerance=0.2) == 2
        assert coll.step_index(2.5, tolerance=0.2) is None
        assert coll.nearest_step_index(10) == 3
        assert ColumnCollection().nearest_step_index(1) is None

    def test_describe(self, coll):
        info = coll.describe()
        assert info["P"]["null_count"] == 1
        assert info["P"]["unit"] == "kN"
        assert info["P"]["max"] == 30.0
        assert "mean" not in info["s"]

    def test_catalog(self):
        c = ColumnCollection({
            "P": Column("P", [0.0, -40.0, None, 30.0], unit="kN", ch="1"),
            "dead": Column("dead", [None, None, None, None], ch="2"),
            "flat": Column("flat", [5.0, 5.0, 5.0, None], ch="3", attrs={"raw_name": "", "unit": "x"}),
            "s": Column("s", ["a", "b", None, "a"], ch="4", attrs={"部位": "柱A"}),
        }, step=[10, 20, 30, 40])
        cat = c.catalog()
        assert cat.columns == ["ch", "name", "unit", "dtype", "n_valid", "null_count", "n_unique", "min", "max",
                               "abs_max", "abs_max_step", "raw_name", "attrs.unit", "部位"]
        assert cat["name"].to_list() == ["P", "dead", "flat", "s"]
        assert cat["ch"].to_list() == ["1", "2", "3", "4"]
        assert cat["n_valid"].to_list() == [3, 0, 3, 3]
        assert cat["n_unique"].to_list() == [3, 0, 1, 2]
        assert cat["min"].to_list() == [-40.0, None, 5.0, None]
        assert cat["abs_max"].to_list() == [40.0, None, 5.0, None]
        assert cat["abs_max_step"].to_list() == [20, None, 10, None]
        assert cat["raw_name"].to_list() == [None, None, "", None]
        assert cat["部位"].to_list() == [None, None, None, "柱A"]
        # 絞り込んだ結果をそのまま select に渡せる
        assert c.select(cat.filter(pl.col("n_unique") <= 1)["name"]).columns == ["dead", "flat"]

    def test_catalog_empty(self):
        cat = ColumnCollection().catalog()
        assert cat.height == 0
        assert cat.schema["abs_max"] == pl.Float64

    @pytest.fixture
    def gauges(self):
        return ColumnCollection({
            "荷重": Column("荷重", [0.0, 100.0, -120.0], unit="kN", ch="@1"),
            "SG-A": Column("SG-A", [0.0, 1500.0, -800.0], unit="με", ch="@2", attrs={"部位": "柱A 上端"}),
            "SG-B": Column("SG-B", [0.0, -300.0, 200.0], unit="µε", ch="@3", attrs={"部位": "柱B"}),
            "@4": Column("@4", [None, None, None], unit="με", ch="@4", attrs={"raw_name": ""}),
            "flat": Column("flat", [7.0, 7.0, 7.0], unit="mN", ch="@5"),
            "memo": Column("memo", ["a", "b", "c"], ch="@6"),
        })

    def test_find_without_conditions_returns_all(self, gauges):
        assert gauges.find() == gauges.columns

    def test_find_text_searches_name_ch_and_attrs(self, gauges):
        assert gauges.find("ｓｇ") == ["SG-A", "SG-B"]              # 全角・大文字小文字を無視
        assert gauges.find("@4") == ["@4"]                            # ch
        assert gauges.find("柱a") == ["SG-A"]                          # attrs の値
        assert gauges.find("柱") == ["SG-A", "SG-B"]
        assert gauges.find("なし") == []

    def test_find_unit_normalizes_width_but_keeps_case(self, gauges):
        assert gauges.find(unit="με") == ["SG-A", "SG-B", "@4"]       # µ（マイクロ記号）も一致
        assert gauges.find(unit=["kN", "mN"]) == ["荷重", "flat"]
        assert gauges.find(unit="MN") == []                           # mN と MN は別物
        assert gauges.find(unit="ｋＮ") == ["荷重"]

    def test_find_by_response_and_dead(self, gauges):
        assert gauges.find(min_abs=1000) == ["SG-A"]
        assert gauges.find(min_abs=100) == ["荷重", "SG-A", "SG-B"]  # 非数値・全欠損の列は含まない
        assert gauges.find(dead=True) == ["@4", "flat"]
        assert gauges.find(dead=False) == ["荷重", "SG-A", "SG-B", "memo"]

    def test_find_combines_conditions_and_where(self, gauges):
        assert gauges.find("sg", unit="με", min_abs=500) == ["SG-A"]
        assert gauges.find(where=lambda c: c.ch in ("@1", "@6")) == ["荷重", "memo"]
        assert gauges.select(gauges.find(unit="με", dead=False)).columns == ["SG-A", "SG-B"]

    def test_missing_column_suggests_names_and_channels(self):
        c = ColumnCollection({"荷重(kN)": Column("荷重(kN)", [1.0], ch="@1"),
                              "SG1": Column("SG1", [1.0], ch="@2")})
        with pytest.raises(KeyError, match=r"列 'ＳＧ１' が存在しません（候補: 'SG1'）"):
            c["ＳＧ１"]
        with pytest.raises(KeyError, match=r"候補: '荷重\(kN\)'"):
            c["荷重"]
        with pytest.raises(KeyError, match=r"'SG1'（ch '@2'）"):
            c["@2"]
        with pytest.raises(KeyError, match=r"チャンネル '2' が存在しません（候補: '@2'）"):
            c.by_ch("2")
        with pytest.raises(KeyError, match=r"'@2'（列 'SG1'）"):
            c.by_ch("sg1")
        with pytest.raises(KeyError, match=r"候補: 'SG1'"):
            c.ops.select(columns=["sg1"])
        with pytest.raises(KeyError, match=r"候補: 'SG1'"):
            c[0]["SG 1"]

    def test_metadata_and_results_are_read_only(self, coll):
        with pytest.raises(TypeError):
            coll.metadata["x"] = 1
        with pytest.raises(TypeError):
            coll.results["x"] = 1
        with pytest.raises(TypeError):
            coll.meta["P"] = ColumnMeta()

    def test_repr(self, coll):
        assert "P [kN]" in repr(coll)


class TestWrite:
    def test_with_column_new(self, coll):
        new = coll.with_column("x", np.arange(4) * 1.5, unit="m")
        assert new.columns == ["P", "d", "s", "x"]
        assert new.units["x"] == "m"
        assert "x" not in coll

    def test_with_column_overwrite_keeps_meta(self, coll):
        c = ColumnCollection({"a": Column("a", [1.0], unit="N", ch="CH1")})
        new = c.with_column("a", [2.0])
        assert new.meta["a"] == ColumnMeta(unit="N", ch="CH1")
        assert new.with_column("a", [3.0], unit=None)["a"].unit is None

    def test_with_column_from_column_object(self, coll):
        new = coll.with_column("y", Column("whatever", [1.0] * 4, unit="s"))
        assert new["y"].unit == "s"

    def test_with_column_length_and_name_checks(self, coll):
        with pytest.raises(ValueError):
            coll.with_column("x", [1.0])
        with pytest.raises(ValueError):
            coll.with_column("time", [1.0] * 4)

    def test_with_meta_and_attrs(self, coll):
        new = coll.with_meta("P", unit="N", ch="CH0").with_attrs("P", note="calibrated")
        assert new.meta["P"] == ColumnMeta(unit="N", ch="CH0", attrs={"note": "calibrated"})
        assert coll["P"].unit == "kN"
        with pytest.raises(KeyError):
            coll.with_meta("nope", unit="N")

    def test_with_metadata_and_result(self, coll):
        result = PointResult("pt", 1.0, 2.0)
        new = coll.with_metadata(a=1).with_result(result)
        assert new.metadata == {"source": "test", "a": 1}
        assert new.results["pt"] is result
        assert "a" not in coll.metadata
        assert not coll.results

    def test_select_drop_rename(self, coll):
        assert coll.select(["d"]).df.columns == ["step", "d"]
        assert coll.drop("P", "s").columns == ["d"]
        renamed = coll.rename({"P": "load"})
        assert renamed.columns == ["load", "d", "s"]
        assert renamed.units["load"] == "kN"
        with pytest.raises(KeyError):
            coll.select(["nope"])
        with pytest.raises(ValueError):
            coll.rename({"P": "step"})

    def test_take(self, coll):
        np.testing.assert_array_equal(coll.take([3, 0]).step, [4, 1])
        np.testing.assert_array_equal(coll.take(np.array([True, False, True, False])).step, [1, 3])
        assert len(coll.take([])) == 0
        with pytest.raises(IndexError):
            coll.take([4])
        with pytest.raises(ValueError):
            coll.take([True, False])

    def test_take_carries_index_columns(self):
        c = ColumnCollection({"a": [1.0, 2.0]}, date=["d1", "d2"])
        assert list(c.take([1]).date) == ["d2"]

    def test_head_tail(self, coll):
        np.testing.assert_array_equal(coll.head(2).step, [1, 2])
        np.testing.assert_array_equal(coll.tail(1).step, [4])

    def test_operations_keep_metadata_and_results(self, coll):
        c = coll.with_result(PointResult("pt", 0.0, 0.0))
        part = c.take([0])
        assert part.metadata == {"source": "test"}
        assert "pt" in part.results


class TestConcat:
    def test_fills_missing_columns(self, coll):
        other = ColumnCollection({"P": [5.0], "z": [1.0]}, step=[9], units={"P": "N", "z": "m"})
        joined = concat([coll, other])
        assert joined.columns == ["P", "d", "s", "z"]
        assert joined.units == {"P": "kN", "d": "mm", "s": None, "z": "m"}
        np.testing.assert_array_equal(joined.step, [1, 2, 3, 4, 9])
        assert joined["z"].null_count() == 4

    def test_empty(self):
        with pytest.raises(ValueError):
            concat([])


class TestRow:
    def test_mapping_and_units(self, coll):
        row = coll[1]
        assert dict(row) == {"step": 2, "P": 10.0, "d": 1.0, "s": "b"}
        assert row.unit("P") == "kN"
        assert row.units == {"P": "kN", "d": "mm", "s": None}
        assert row.to_dict()["step"] == 2
        with pytest.raises(KeyError):
            row["nope"]

    def test_repr_shows_units(self, coll):
        assert "P=10.0 kN" in repr(coll[1])
