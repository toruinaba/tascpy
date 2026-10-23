import pytest
import io
from pathlib import Path
from tascpy.io.file_io import load_collection, save_collection
from tascpy.io.formats import register_format, get_format
from tascpy.core.collection import ColumnCollection
import numpy as np

def test_load_from_stream():
    data = "DATA\nCH\tcol1\nNAME\tcol1\nUNIT\t\n1\t10.0\n2\t20.0"
    stream = io.StringIO(data)
    collection = load_collection(stream, format_name="standard", data_start_col=1, date_col=None, time_col=None)
    assert len(collection) == 2
    assert "col1" in collection.columns

def test_load_from_string_path_and_missing_file():
    with pytest.raises(FileNotFoundError):
        load_collection("nonexistent_file.txt")

def test_formatting_edge_cases():
    # no ch row, name_row == ch_row
    data = "1\t10.0"
    stream = io.StringIO(data)
    collection = load_collection(stream, format_name="standard", ch_row=99, name_row=99, unit_row=99, data_start_row=0, data_start_col=1, date_col=None, time_col=None)
    assert len(collection) == 1

def test_empty_data_start_row():
    data = "DATA\nCH\tCH1\nNAME\tcol1\nUNIT\t\n"
    stream = io.StringIO(data)
    collection = load_collection(stream, format_name="standard", data_start_row=5, data_start_col=1, date_col=None, time_col=None)
    assert len(collection) == 0

def test_step_keeps_non_integer_values():
    data = "DATA\nCH\tCH1\nNAME\tcol1\nUNIT\t\nNone\t10.0\ninvalid\t20.0\n\t30.0"
    collection = load_collection(io.StringIO(data), format_name="standard", data_start_col=1, date_col=None, time_col=None)
    assert list(collection.step) == [None, "invalid", None]


@pytest.mark.parametrize("cells, expected", [
    (["1", "2"], [1, 2]),
    (["0.5", "1.5"], [0.5, 1.5]),
])
def test_step_numeric_types(cells, expected):
    data = "DATA\nCH\tCH1\nNAME\tcol1\nUNIT\t\n" + "".join(f"{c}\t1\n" for c in cells)
    collection = load_collection(io.StringIO(data), format_name="standard", data_start_col=1, date_col=None, time_col=None)
    np.testing.assert_array_equal(collection.step, expected)

def test_missing_date_time_cols():
    data = "DATA\nCH\tCH1\nNAME\tcol1\nUNIT\t\n1\t10.0"
    stream = io.StringIO(data)
    collection = load_collection(stream, format_name="standard", date_col=99, time_col=99, data_start_col=1)
    assert len(collection) == 1

def test_selected_columns_and_jagged_rows():
    data = "DATA\nCH\tCH1\tCH2\nNAME\tcol1\tcol2\nUNIT\t\t\n1\t10.0\t20.0\n2\t15.0" # row 2 is missing col2
    stream = io.StringIO(data)
    collection = load_collection(stream, format_name="standard", selected_columns=["col1"], data_start_col=1, date_col=None, time_col=None)
    assert "col1" in collection.columns
    assert "col2" not in collection.columns
    
    stream = io.StringIO(data)
    collection2 = load_collection(stream, format_name="standard", data_start_col=1, date_col=None, time_col=None)
    assert collection2["col2"][-1] is None
    assert np.isnan(collection2["col2"].values[-1])

def test_missing_tokens_and_blank_units():
    data = "DATA\nCH\tCH1\tCH2\nNAME\tcol1\tcol2\nUNIT\tkN\t\n1\t10.0\t*****\n2\tnone\t5"
    collection = load_collection(io.StringIO(data), format_name="standard", data_start_col=1, date_col=None, time_col=None)
    assert collection["col1"].unit == "kN"
    assert collection["col2"].unit is None
    assert collection["col1"].ch == "CH1"
    assert collection["col1"].to_list() == [10.0, None]
    assert collection["col2"].to_list() == [None, 5.0]
    assert collection["col1"].is_numeric

def test_date_time_are_index_columns():
    data = "DATA\nCH\tDATE\tTIME\tCH1\nNAME\tDATE\tTIME\tcol1\nUNIT\t\t\tkN\n1\t2023/01/01\t00:00:00\t1.0\n2\t2023/01/01\t00:00:01\t2.0"
    collection = load_collection(io.StringIO(data), format_name="standard")
    assert collection.columns == ["col1"]
    assert list(collection.date) == ["2023/01/01", "2023/01/01"]
    assert list(collection.time) == ["00:00:00", "00:00:01"]
    filtered = collection.ops.filter_by_value("col1", 2.0).end()
    assert list(filtered.time) == ["00:00:01"]

def test_save_string_path_and_missing_values(tmp_path):
    out_path = str(tmp_path / "out_str.txt")
    from tascpy.core.column import Column
    col = ColumnCollection({"C1": Column("C1", [None, True], ch="CH1")}, step=[1, 2])
    save_collection(col, out_path, format_name="standard")
    
    loaded = load_collection(out_path, format_name="standard")
    assert loaded["C1"][0] is None
    assert loaded["C1"][1] is True

def _load_one_column(*cells):
    data = "DATA\nCH\tCH1\nNAME\tc\nUNIT\t\n" + "".join(f"{i}\t{v}\n" for i, v in enumerate(cells))
    return load_collection(io.StringIO(data), format_name="standard", data_start_col=1, date_col=None, time_col=None)["c"]


def test_value_conversion():
    assert _load_one_column("*******", "*", "none", "NaN", "10", "10.5").to_list() == [None, None, None, None, 10.0, 10.5]
    assert _load_one_column("True", "false").to_list() == [True, False]
    assert _load_one_column("abc", "1").to_list() == ["abc", "1"]


def test_blank_lines_are_skipped():
    data = "DATA\nCH\tCH1\nNAME\tc\nUNIT\t\n1\t1\n\n2\t2\n\n\n"
    loaded = load_collection(io.StringIO(data), format_name="standard", data_start_col=1, date_col=None, time_col=None)
    assert len(loaded) == 2


def test_header_names_fallback_and_dedupe():
    data = "DATA\nCH\tC1\tC2\tC3\tC4\tC5\nNAME\tA\tA\t\ttime\nUNIT\tkN\n1\t1\t2\t3\t4\t5\t6\n"
    with pytest.warns(UserWarning):
        loaded = load_collection(io.StringIO(data), format_name="standard", data_start_col=1, date_col=None, time_col=None)
    # 名前が空欄なら ch、名前行が短ければ ch で補う。重複・予約名には接尾辞。ヘッダーのない列は無視
    assert loaded.columns == ["A", "A_2", "C3", "time_2", "C5"]
    assert loaded.units == {"A": "kN", "A_2": None, "C3": None, "time_2": None, "C5": None}
    assert loaded["C5"].to_list() == [5.0]


def test_unknown_selected_column():
    data = "DATA\nCH\tCH1\nNAME\tc\nUNIT\t\n1\t1\n"
    with pytest.raises(KeyError):
        load_collection(io.StringIO(data), format_name="standard", selected_columns=["x"], data_start_col=1,
                        date_col=None, time_col=None)


def test_round_trip_keeps_names_ch_step_and_quoted_values(tmp_path):
    from tascpy.core.column import Column
    original = ColumnCollection(
        {"Force1": Column("Force1", [1.0, None], unit="kN", ch="CH0"), "note": ["a\tb", "x"],
         "flag": [True, False], "nochannel": [3.0, 4.0]},
        step=[0.1, 0.2], date=["2020/1/1", "2020/1/2"],
    )
    path = tmp_path / "rt.txt"
    save_collection(original, path)
    loaded = load_collection(path)
    assert loaded.columns == original.columns
    assert loaded.meta == original.meta
    assert loaded.df.equals(original.df)


def test_save_unencodable_text_keeps_existing_file(tmp_path):
    from tascpy.core.column import Column
    path = tmp_path / "out.txt"
    path.write_text("existing", encoding="utf-8")
    collection = ColumnCollection({"E": Column("E", [1.0], unit="kN·mm")})
    with pytest.raises(ValueError, match="encoding='utf-8'"):
        save_collection(collection, path)
    assert path.read_text(encoding="utf-8") == "existing"
    assert list(tmp_path.iterdir()) == [path]

    save_collection(collection, path, encoding="utf-8")
    assert load_collection(path, encoding="utf-8")["E"].unit == "kN·mm"


def test_save_keeps_file_permissions(tmp_path):
    import os
    path = tmp_path / "out.txt"
    path.write_text("x")
    os.chmod(path, 0o640)
    save_collection(ColumnCollection({"a": [1.0]}), path)
    assert os.stat(path).st_mode & 0o777 == 0o640


def test_register_format_fills_layout_defaults(monkeypatch):
    from tascpy.io import formats
    monkeypatch.setattr(formats, "FILE_FORMATS", dict(formats.FILE_FORMATS))
    register_format("test_semicolon", {"delimiter": ";"})
    config = get_format("test_semicolon")
    assert config["delimiter"] == ";"
    assert config["data_start_row"] == 4
    assert config["encoding"] == "utf-8"

def test_formats_registry():
    register_format("custom", {"delimiter": ","})
    fmt = get_format("custom")
    assert fmt["delimiter"] == ","
    
    with pytest.raises(KeyError):
        get_format("unregistered")
