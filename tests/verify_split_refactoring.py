
import sys
import os
import numpy as np
import pytest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.core.step import Step
import tascpy.operations.core.split # Register operations

def create_test_collection():
    c = ColumnCollection(step=[], columns={})
    c.step = Step(values=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    
    # Val: [0, 10, 20, ..., 90]
    vals = [float(i*10) for i in range(10)]
    c.add_column("Val", NumberColumn(None, "Val", "unit", values=vals))
    
    return c

def test_split_by_integers():
    c = create_test_collection()
    # markers: 0, 1, 0, 1 ...
    markers = [0 if i % 2 == 0 else 1 for i in range(10)]
    
    res = c.ops.split_by_integers(markers=markers)
    
    assert len(res) == 2
    
    # Group 0: 0, 2, 4, 6, 8 -> Val: 0, 20, 40, 60, 80
    expected_0 = [0.0, 20.0, 40.0, 60.0, 80.0]
    np.testing.assert_array_almost_equal(res[0]["Val"].values, expected_0)
    
    # Group 1: 1, 3, 5, 7, 9 -> Val: 10, 30, 50, 70, 90
    expected_1 = [10.0, 30.0, 50.0, 70.0, 90.0]
    np.testing.assert_array_almost_equal(res[1]["Val"].values, expected_1)
    
    print("Pass: split_by_integers")

def test_split_at_indices():
    c = create_test_collection()
    # Length 10. Split at 3, 7.
    # Segments: 0:3, 3:7, 7:10
    # [0,1,2], [3,4,5,6], [7,8,9]
    
    res = c.ops.split_at_indices(indices=[3, 7])
    
    assert len(res) == 3
    
    # Seg 1
    expected_1 = [0.0, 10.0, 20.0]
    np.testing.assert_array_almost_equal(res[0]["Val"].values, expected_1)
    
    # Seg 2
    expected_2 = [30.0, 40.0, 50.0, 60.0]
    np.testing.assert_array_almost_equal(res[1]["Val"].values, expected_2)
    
    # Seg 3
    expected_3 = [70.0, 80.0, 90.0]
    np.testing.assert_array_almost_equal(res[2]["Val"].values, expected_3)
    
    print("Pass: split_at_indices")

if __name__ == "__main__":
    test_split_by_integers()
    test_split_at_indices()
