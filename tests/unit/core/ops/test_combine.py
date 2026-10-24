
import pytest
import numpy as np
from collections.abc import Mapping
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column

@pytest.fixture
def sample_collection():
    """Create a sample collection for testing"""
    # Create valid step data (0 to 9)
    step_data = list(range(10))
    
    # Data columns
    columns = {
        "col1": Column("col1", [10.0] * 10),
        "col2": Column("col2", [20.0] * 10),
        "cond": Column("cond", [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    }
    
    # Initialize with required arguments
    c = ColumnCollection(columns, step=step_data)
    
    # Add extra column if needed, or just use what we have
    # The tests use col1, col2, cond.
    # Some tests might assume 'step' column is accessible via c.step or as a column.
    # The ColumnCollection logic usually exposes step as property.
    
    return c

def test_switch_by_step_structure(sample_collection):
    """Test switch_by_step injects columns and metadata correctly"""
    result = sample_collection.ops.switch_by_step("col1", "col2", threshold=5, compare_mode="index"
    ).end()
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "switch" in c]
    assert len(result_col) == 1
    
    col_name = result_col[0]
    assert isinstance(result[col_name].attrs, Mapping)

def test_blend_by_step_structure(sample_collection):
    """Test blend_by_step structural properties"""
    result = sample_collection.ops.blend_by_step("col1", "col2", start=2, end=7
    ).end()
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "blend" in c]
    assert len(result_col) == 1
    
    assert isinstance(result[result_col[0]].attrs, Mapping)

def test_conditional_select_structure(sample_collection):
    """Test conditional_select structural properties"""
    result = sample_collection.ops.conditional_select("col1", "col2", "cond", threshold=0.5
    ).end()
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "select" in c]
    assert len(result_col) == 1

def test_sum_columns_structure(sample_collection):
    """Test sum_columns structural properties"""
    result = sample_collection.ops.sum_columns(columns=["col1", "col2"]).end()
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "sum" in c]
    assert len(result_col) == 1

def test_average_columns_structure(sample_collection):
    """Test average_columns structural properties"""
    result = sample_collection.ops.average_columns(columns=["col1", "col2"]).end()
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "average" in c]
    assert len(result_col) == 1

def test_sum_columns_values_and_missing():
    col = ColumnCollection({"a": [1.0, 2.0, None], "b": [4.0, 5.0, 6.0]})
    result = col.ops.sum_columns(["a", "b"], result_column="s").end()
    np.testing.assert_array_equal(result["s"].values, [5.0, 7.0, np.nan])


def test_average_columns_values():
    col = ColumnCollection({"a": [10.0, 20.0, None], "b": [30.0, 40.0, None]})
    result = col.ops.average_columns(["a", "b"], result_column="m").end()
    np.testing.assert_array_equal(result["m"].values, [20.0, 30.0, np.nan])


@pytest.mark.parametrize("method", ["sum_columns", "average_columns"])
def test_sum_and_average_require_columns(method):
    col = ColumnCollection({"a": [1.0, 2.0]})
    with pytest.raises(ValueError, match="対象の列が指定されていません"):
        getattr(col.ops, method)([])


def test_custom_combine_structure(sample_collection):
    """Test custom_combine structural properties"""
    def my_add(x, y):
        return x + y + 1
        
    result = sample_collection.ops.custom_combine("col1", "col2", combine_func=my_add, func_name="my_add"
    ).end()
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "my_add" in c]
    assert len(result_col) == 1

