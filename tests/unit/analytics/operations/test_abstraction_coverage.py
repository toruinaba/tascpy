import pytest
import numpy as np
from typing import Dict, Any, Union
from tascpy.core.collection import ColumnCollection
from tascpy.core.step import Step
from tascpy.core.column import Column, NumberColumn
from tascpy.analytics.operations.abstraction import (
    inject_columns,
    inject_step_values,
    handle_missing_values,
    store_result,
    store_xy_result,
    store_point_result,
    store_multiple_results,
    process_by_group,
)

@pytest.fixture
def sample_collection():
    return ColumnCollection(
        step=Step([1, 2, 3]),
        columns={
            "A": NumberColumn("CH1", "A", "u1", [10.0, 20.0, 30.0]),
            "B": NumberColumn("CH2", "B", "u2", [1.1, np.nan, 3.3]),
            "grp": NumberColumn("CH3", "grp", "", [1.0, 1.0, 2.0]),
        }
    )

def test_inject_columns_raw_data_mode():
    @inject_columns(num_inputs=1, cast_to_numpy=True)
    def dummy_func(col1, extra_arg):
        return isinstance(col1, np.ndarray), extra_arg
    
    # Passing a list directly should trigger raw data mode
    is_np, arg = dummy_func([1, 2, 3], "test")
    assert is_np is True
    assert arg == "test"

    @inject_columns(num_inputs=1, cast_to_numpy=False)
    def dummy_func_no_cast(col1):
        return col1

    assert dummy_func_no_cast([1, 2, 3]) == [1, 2, 3]

def test_inject_columns_with_step():
    @inject_columns(num_inputs=1, include_step=True)
    def dummy_func(steps, col1):
        return steps, col1
    
    col = ColumnCollection(step=Step([1, 2]), columns={"A": NumberColumn("A", "A", "", [10, 20])})
    
    step_val, col1_val = dummy_func(col, "A")
    np.testing.assert_array_equal(step_val, [1, 2])
    np.testing.assert_array_equal(col1_val, [10, 20])

def test_inject_columns_column_arg_pos(sample_collection):
    @inject_columns(columns_arg="cols", columns_arg_pos=0)
    def dummy_func(data_dict, *args, **kwargs):
        return data_dict, args, kwargs

    # test columns_arg passed via positional
    data_dict, args, kwargs = dummy_func(sample_collection, ["A"])
    assert "A" in data_dict
    assert "B" not in data_dict

def test_inject_columns_list_casting(sample_collection):
    # force a column with list values
    sample_collection.columns["C"] = Column("CHC", "C", "", [1, 2, 3])
    
    @inject_columns(num_inputs=1, cast_to_numpy=True)
    def dummy_func(val):
        return val

    res = dummy_func(sample_collection, "C")
    assert isinstance(res, np.ndarray)

def test_inject_step_values_raw_mode():
    @inject_step_values(cast_to_numpy=True)
    def dummy_func(steps, multiplier):
        return steps * multiplier

    res = dummy_func([1, 2, 3], 2)
    np.testing.assert_array_equal(res, [2, 4, 6])
    assert isinstance(res, np.ndarray)

def test_handle_missing_values_strict():
    @handle_missing_values(strategy="strict")
    def dummy_func(val1):
        return val1 * 2

    # None in list
    res = dummy_func([1.0, None, 3.0])
    assert len(res) == 3
    assert np.isnan(res).all()

    # None in object array
    res = dummy_func(np.array([1.0, None, 3.0], dtype=object))
    assert len(res) == 3
    assert np.isnan(res).all()

def test_handle_missing_values_nan_exceptions():
    @handle_missing_values(strategy="nan")
    def dummy_func(val1):
        assert isinstance(val1[0], Uncastable)
        return True

    class Uncastable:
        pass

    # Should append original arg if exception during casting, and then inner function checks it.
    res = dummy_func(np.array([Uncastable(), Uncastable()], dtype=object))
    assert res is True

    # Test list uncastable
    res2 = dummy_func([Uncastable()])
    assert res2 is True

def test_store_result_raw_mode():
    @store_result(result_naming="out")
    def dummy_func(data, multiplier):
        return data * multiplier

    res = dummy_func(np.array([1, 2, 3]), 2)
    np.testing.assert_array_equal(res, [2, 4, 6])

def test_store_result_tuple_with_metadata(sample_collection):
    @store_result()
    def dummy_func(col, name):
        return np.array([1, 2, 3]), {"extra": "meta"}

    res = dummy_func(sample_collection, "A")
    assert list(res.columns["dummy_func(A)"].values) == [1, 2, 3] # fallback logic generates 'dummy_func(args[0])' if result_column=None and len(args)>0
    assert res.metadata["extra"] == "meta"

def test_store_result_naming_fallbacks(sample_collection):
    # Callable naming
    def custom_namer(func_name, *args, **kwargs):
        return f"{func_name}_custom"
        
    @store_result(result_naming=custom_namer)
    def my_func(col):
        return [1, 2, 3]
        
    res = my_func(sample_collection)
    assert "my_func_custom" in res.columns

    # Formatter failure fallback
    @store_result(result_naming="out_{invalid_key}")
    def failed_fmt(col):
        return [1, 2, 3]

    res2 = failed_fmt(sample_collection)
    names = list(res2.columns.keys())
    assert any(n.startswith("result_") for n in names)

def test_store_xy_result_raw_mode():
    @store_xy_result()
    def my_func(data):
        return data * 2, data * 3
    
    res1, res2 = my_func(np.array([1, 2]))
    # Wait, my_func returns a tuple. If raw mode, it just returns what target_func returns.
    assert np.array_equal(res1, [2, 4])

def test_store_xy_result_metadata_exception(sample_collection):
    def bad_injector(args, kwargs, res):
        raise ValueError("BAD")
        
    @store_xy_result(inject_metadata=bad_injector)
    def my_func(col):
        return [1], [2]

    with pytest.raises(ValueError, match="BAD"):
        my_func(sample_collection)

def test_store_point_result_with_metadata(sample_collection):
    def injector(args, kwargs, res):
        return {"point_meta": 1}

    @store_point_result(inject_metadata=injector)
    def my_func(col):
        # is_valid, x, y, extra
        return True, 10.0, 20.0, {"inner": 2}
        
    res = my_func(sample_collection)
    assert "point" in res._results
    assert res._results["point"].metadata["inner"] == 2
    assert res.metadata["point_meta"] == 1

def test_store_multiple_results(sample_collection):
    config = [
        {"type": "scalar", "name": "res_E", "index": 0},
        {"type": "point", "name": "res_P", "x_index": 1, "y_index": 2}
    ]

    @store_multiple_results(results=config)
    def my_func(col):
        return 100.0, 10.0, 20.0

    # Test Collection mode
    res = my_func(sample_collection)
    assert "res_E" in res._results
    assert "res_P" in res._results
    assert res._results["res_E"].value == 100.0
    assert res._results["res_P"].x == 10.0

    # Test Raw mode
    raw_res = my_func(np.array([1, 2, 3]))
    assert raw_res == (100.0, 10.0, 20.0)

def test_process_by_group(sample_collection):
    config = [
        {"name": "res_mean", "index": 0},
    ]

    @process_by_group(group_column_arg="group", default_group_column="grp", output_columns=config)
    def group_func(col, target):
        m = np.mean(col[target].values)
        return m

    res = group_func(sample_collection, "A")
    # grp has [1.0, 2.0]
    # For 1.0, A is [10.0, 20.0] -> mean = 15.0
    # For 2.0, A is [30.0] -> mean = 30.0
    
    assert list(res.step.values) == [1.0, 2.0]
    assert "res_mean" in res.columns
    np.testing.assert_allclose(res.columns["res_mean"].values, [15.0, 30.0])

    # Raw Mode is tested with group_func_raw

    # But we can test raw mode correctly
    @process_by_group(group_column_arg="group", default_group_column="grp", output_columns=config)
    def group_func_raw(col):
        return col * 2

    assert group_func_raw(10) == 20
