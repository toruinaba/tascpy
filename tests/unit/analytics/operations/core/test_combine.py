
import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.analytics.operations.core.combine import (
    switch_by_step,
    blend_by_step,
    conditional_select,
    sum_columns,
    average_columns,
    custom_combine,
)

@pytest.fixture
def sample_collection():
    """Create a sample collection for testing"""
    # Create valid step data (0 to 9)
    step_data = list(range(10))
    
    # Data columns
    columns = {
        "col1": Column(ch=None, name="col1", unit=None, values=[10.0] * 10),
        "col2": Column(ch=None, name="col2", unit=None, values=[20.0] * 10),
        "cond": Column(ch=None, name="cond", unit=None, values=[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    }
    
    # Initialize with required arguments
    c = ColumnCollection(step=step_data, columns=columns)
    
    # Add extra column if needed, or just use what we have
    # The tests use col1, col2, cond.
    # Some tests might assume 'step' column is accessible via c.step or as a column.
    # The ColumnCollection logic usually exposes step as property.
    
    return c

def test_switch_by_step_structure(sample_collection):
    """Test switch_by_step injects columns and metadata correctly"""
    result = switch_by_step(
        sample_collection, "col1", "col2", threshold=5, compare_mode="index"
    )
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "switch" in c]
    assert len(result_col) == 1
    
    col_name = result_col[0]
    metadata = result[col_name].metadata
    assert isinstance(metadata, dict)

def test_blend_by_step_structure(sample_collection):
    """Test blend_by_step structural properties"""
    result = blend_by_step(
        sample_collection, "col1", "col2", start=2, end=7
    )
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "blend" in c]
    assert len(result_col) == 1
    
    metadata = result[result_col[0]].metadata
    assert isinstance(metadata, dict)

def test_conditional_select_structure(sample_collection):
    """Test conditional_select structural properties"""
    result = conditional_select(
        sample_collection, "col1", "col2", "cond", threshold=0.5
    )
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "select" in c]
    assert len(result_col) == 1

def test_sum_columns_structure(sample_collection):
    """Test sum_columns structural properties"""
    result = sum_columns(sample_collection, columns=["col1", "col2"])
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "sum" in c]
    assert len(result_col) == 1

def test_average_columns_structure(sample_collection):
    """Test average_columns structural properties"""
    result = average_columns(sample_collection, columns=["col1", "col2"])
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "average" in c]
    assert len(result_col) == 1

def test_custom_combine_structure(sample_collection):
    """Test custom_combine structural properties"""
    def my_add(x, y):
        return x + y + 1
        
    result = custom_combine(
        sample_collection, "col1", "col2", combine_func=my_add, func_name="my_add"
    )
    
    assert isinstance(result, ColumnCollection)
    result_col = [c for c in result.columns if "my_add" in c]
    assert len(result_col) == 1

