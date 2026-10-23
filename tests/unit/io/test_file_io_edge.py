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

def test_step_parsing_edge_cases():
    data = "DATA\nCH\tCH1\nNAME\tcol1\nUNIT\t\nNone\t10.0\ninvalid\t20.0\n\t30.0"
    stream = io.StringIO(data)
    collection = load_collection(stream, format_name="standard", data_start_col=1, date_col=None, time_col=None)
    # Should use row_idx + 1: 1, 2, 3
    np.testing.assert_array_equal(collection.step, [1, 2, 3])

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

def test_convert_value_cases():
    from tascpy.io.file_io import _convert_value
    assert _convert_value("*******") is None
    assert _convert_value("*") is None
    assert _convert_value("True") is True
    assert _convert_value("False") is False
    assert _convert_value("10") == 10
    assert _convert_value("10.5") == 10.5
    assert _convert_value("NotANumber") == "NotANumber"

def test_formats_registry():
    register_format("custom", {"delimiter": ","})
    fmt = get_format("custom")
    assert fmt["delimiter"] == ","
    
    with pytest.raises(KeyError):
        get_format("unregistered")
