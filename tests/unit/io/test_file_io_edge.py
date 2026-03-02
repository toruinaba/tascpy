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
    np.testing.assert_array_equal(collection.step.values, [1, 2, 3])

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
    assert collection2["col2"].values[-1] is None

def test_auto_detect_types():
    data = "DATA\nCH\tCH1\nNAME\tcol1\nUNIT\t\n1\t10.0"
    stream = io.StringIO(data)
    collection = load_collection(stream, format_name="standard", auto_detect_types=True, data_start_col=1, date_col=None, time_col=None)
    assert type(collection["col1"]).__name__ == "NumberColumn"

def test_save_string_path_and_missing_values(tmp_path):
    out_path = str(tmp_path / "out_str.txt")
    from tascpy.core.step import Step
    from tascpy.core.column import Column
    col = ColumnCollection(
        step=Step([1, 2]),
        columns={"C1": Column("CH1", "C1", "", [None, True])}
    )
    save_collection(col, out_path, format_name="standard")
    
    loaded = load_collection(out_path, format_name="standard")
    assert loaded["C1"][0] is None
    assert loaded["C1"][1] is True

def test_convert_value_cases():
    from tascpy.io.file_io import _convert_value
    assert _convert_value("*******") is None
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
