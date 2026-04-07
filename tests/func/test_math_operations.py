import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn, StringColumn
import tascpy.analytics.operations.core.math  # Ensure ops are registered

def test_average_across():
    steps = [1, 2, 3, 4]
    
    col1 = NumberColumn("CH1", "A", "V", [1.0, 2.0, np.nan, 4.0])
    col2 = NumberColumn("CH2", "B", "V", [1.0, 4.0, 6.0, np.nan])
    col3 = NumberColumn("CH3", "C", "V", [1.0, np.nan, np.nan, np.nan])
    
    columns = {
        "A": col1,
        "B": col2,
        "C": col3
    }
    
    collection = ColumnCollection(steps, columns)
    
    # 1. ignore_nan=True (default)
    result1 = collection.ops.average_across("A", "B", "C", result_column="avg_ignore")
    assert "avg_ignore" in result1.columns
    
    avg_vals1 = result1["avg_ignore"].values
    # row0: [1, 1, 1] -> 1.0
    # row1: [2, 4, nan] -> (2 + 4) / 2 = 3.0
    # row2: [nan, 6, nan] -> 6.0
    # row3: [4, nan, nan] -> 4.0
    np.testing.assert_allclose(avg_vals1, [1.0, 3.0, 6.0, 4.0])
    
    # 2. ignore_nan=False
    result2 = collection.ops.average_across("A", "B", "C", result_column="avg_strict", ignore_nan=False)
    assert "avg_strict" in result2.columns
    
    avg_vals2 = result2["avg_strict"].values
    # row0: [1, 1, 1] -> 1.0
    # row1: [2, 4, nan] -> nan
    # row2: [nan, 6, nan] -> nan
    # row3: [4, nan, nan] -> nan
    assert avg_vals2[0] == 1.0
    assert np.isnan(avg_vals2[1])
    assert np.isnan(avg_vals2[2])
    assert np.isnan(avg_vals2[3])
    
    # 3. Automatic naming
    result3 = collection.ops.average_across("A", "B")
    assert any(col.startswith("average_across") for col in result3.columns)

def test_average_across_string_coercion():
    steps = [1, 2, 3]
    
    col1 = StringColumn("CH1", "A", "V", ["1.0", "none", "3.0"])
    col2 = StringColumn("CH2", "B", "V", ["none", "2.0", "na"])
    
    columns = {
        "A": col1,
        "B": col2
    }
    
    collection = ColumnCollection(steps, columns)
    
    result = collection.ops.average_across("A", "B", result_column="avg_str")
    avg_vals = result["avg_str"].values
    
    # row0: ["1.0", "none"] -> 1.0
    # row1: ["none", "2.0"] -> 2.0
    # row2: ["3.0", "na"] -> 3.0
    np.testing.assert_allclose(avg_vals, [1.0, 2.0, 3.0])
