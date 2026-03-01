
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

def test_switch_by_step_basic(sample_collection):
    """Test switch_by_step using index"""
    result = switch_by_step(
        sample_collection,
        "col1",
        "col2",
        threshold=5,
        compare_mode="index",
        by_step_value=False
    )
    
    # Check result
    result_col = [c for c in result.columns if "switch" in c][0]
    values = result[result_col].values
    
    # Index < 5 -> col1 (10)
    assert np.all(np.array(values[:5]) == 10)
    # Remaining values -> col2 (20)
    assert np.all(np.array(values[5:]) == 20)

def test_switch_by_step_value(sample_collection):
    """Test switch_by_step using step value"""
    # Steps are 0, 1, ..., 9. Threshold 5 means steps < 5 use col1
    result = switch_by_step(
        sample_collection,
        "col1",
        "col2",
        threshold=5,
        compare_mode="value",
        by_step_value=True
    )
    
    result_col = [c for c in result.columns if "switch" in c][0]
    values = result[result_col].values
    
    # Steps 0..4 (value < 5) -> col1 (10)
    assert np.all(np.array(values[:5]) == 10)
    # Steps 5..9 (value >= 5) -> col2 (20)
    assert np.all(np.array(values[5:]) == 20)

def test_blend_by_step_linear(sample_collection):
    """Test blend_by_step with linear blending"""
    # Blend from index 2 to 7
    # index < 2: col1 (10)
    # index > 7: col2 (20)
    # 2 <= index <= 7: blended linearly
    
    result = blend_by_step(
        sample_collection,
        "col1",
        "col2",
        start=2,
        end=7,
        compare_mode="index",
        by_step_value=False,
        blend_method="linear"
    )
    
    result_col = [c for c in result.columns if "blend" in c][0]
    values = result[result_col].values
    
    # Before range
    assert values[1] == 10
    
    # At start (t=0)
    assert values[2] == 10.0
    
    # At end (t=1)
    assert values[7] == 20.0
    
    # After range
    assert values[8] == 20
    
    # Midpoint: index 4.5 -> But index is integer.
    # index 4. start=2, end=7. len=5. (4-2)/5 = 0.4
    # value = 10 * (1-0.4) + 20 * 0.4 = 6 + 8 = 14
    assert values[4] == 14.0

def test_conditional_select(sample_collection):
    """Test conditional_select"""
    # cond column: [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    # condition: > 0.5
    # indices 0-4 (val=0) -> False -> col2 (20)
    # indices 5-9 (val=1) -> True -> col1 (10)
    
    result = conditional_select(
        sample_collection,
        "col1",
        "col2",
        "cond",
        threshold=0.5,
        compare=">"
    )
    
    result_col = [c for c in result.columns if "select" in c][0]
    values = result[result_col].values
    
    assert np.all(np.array(values[:5]) == 20)
    assert np.all(np.array(values[5:]) == 10)

def test_sum_columns(sample_collection):
    """Test sum_columns"""
    result = sum_columns(
        sample_collection,
        columns=["col1", "col2"]
    )
    
    result_col = [c for c in result.columns if "sum" in c][0]
    values = result[result_col].values
    
    # 10 + 20 = 30
    assert np.all(np.array(values) == 30)

def test_average_columns(sample_collection):
    """Test average_columns"""
    result = average_columns(
        sample_collection,
        columns=["col1", "col2"]
    )
    
    result_col = [c for c in result.columns if "average" in c][0]
    values = result[result_col].values
    
    # (10 + 20) / 2 = 15
    assert np.all(np.array(values) == 15)

def test_custom_combine(sample_collection):
    """Test custom_combine with lambda"""
    def my_add(x, y):
        return x + y + 1
        
    result = custom_combine(
        sample_collection,
        "col1",
        "col2",
        combine_func=my_add,
        func_name="my_add"
    )
    
    result_col = [c for c in result.columns if "my_add" in c][0]
    values = result[result_col].values
    
    # 10 + 20 + 1 = 31
    assert np.all(np.array(values) == 31)

