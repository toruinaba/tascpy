import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column

def test_average_columns():
    steps = [1, 2, 3, 4]
    
    col1 = Column("A", [1.0, 2.0, np.nan, 4.0], unit="V", ch="CH1")
    col2 = Column("B", [1.0, 4.0, 6.0, np.nan], unit="V", ch="CH2")
    col3 = Column("C", [1.0, np.nan, np.nan, np.nan], unit="V", ch="CH3")
    
    columns = {
        "A": col1,
        "B": col2,
        "C": col3
    }
    
    collection = ColumnCollection(columns, step=steps)
    
    # 1. ignore_nan=True (default)
    result1 = collection.ops.average_columns(["A", "B", "C"], result_column="avg_ignore").end()
    assert "avg_ignore" in result1.columns
    
    avg_vals1 = result1["avg_ignore"].values
    # row0: [1, 1, 1] -> 1.0
    # row1: [2, 4, nan] -> (2 + 4) / 2 = 3.0
    # row2: [nan, 6, nan] -> 6.0
    # row3: [4, nan, nan] -> 4.0
    np.testing.assert_allclose(avg_vals1, [1.0, 3.0, 6.0, 4.0])
    assert result1["avg_ignore"].unit == "V"
    
    # 2. ignore_nan=False
    result2 = collection.ops.average_columns(["A", "B", "C"], result_column="avg_strict", ignore_nan=False).end()
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
    result3 = collection.ops.average_columns(["A", "B"]).end()
    assert "average_columns(A,B)" in result3.columns

def test_average_columns_rejects_non_numeric_columns():
    collection = ColumnCollection({"A": [1.0, 2.0], "S": ["x", "y"]}, step=[1, 2])

    with pytest.raises(TypeError, match="数値列ではありません"):
        collection.ops.average_columns(["A", "S"])
    # 列を省略した場合は数値列だけが対象
    result = collection.ops.average_columns(result_column="avg").end()
    np.testing.assert_allclose(result["avg"].values, [1.0, 2.0])
    result = collection.ops.sum_columns(result_column="total").end()
    np.testing.assert_allclose(result["total"].values, [1.0, 2.0])
