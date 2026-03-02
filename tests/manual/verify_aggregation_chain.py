import sys
from pathlib import Path
import pytest
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.column import Column
from tascpy.core.step import Step
from tascpy.core.collection import ColumnCollection
from tascpy.analytics.operations.proxy import CollectionOperations

def test_aggregation_chaining_dict():
    print("\n[1] Testing chaining after dict-returning aggregation (max)")
    
    step = Step([0.1, 0.2, 0.3])
    c = ColumnCollection(step, {
        "col1": [1.0, 5.0, 3.0],
        "col2": [10.0, 20.0, 5.0]
    })
    
    # max() returns a dict like {'col1': 5.0, 'col2': 20.0}
    # With our change, it should return a CollectionOperations wrapping a single-row collection.
    result_ops = c.ops.max()
    
    print(f"Result type: {type(result_ops)}")
    assert isinstance(result_ops, CollectionOperations)
    
    result_col = result_ops.end()
    print(f"Result columns: {result_col.columns.keys()}")
    print(f"Result step: {result_col.step.values}")
    
    assert "col1" in result_col.columns
    assert result_col["col1"].values[0] == 5.0
    assert result_col.step.values[0] == "max"
    
    # Test chaining
    # Convert to numeric (should be already numeric, but checking method availability)
    chained = c.ops.max().to_numeric()
    assert isinstance(chained, CollectionOperations)
    print("Chaining successful.")

def test_aggregation_chaining_scalar():
    print("\n[2] Testing chaining after scalar-returning aggregation")
    
    # We need a method that returns a scalar.
    # Let's mock one or find one. 'abs_max' returns dict if called on collection?
    # collection.mean() returns dict.
    
    # Let's register a dummy operation that returns a scalar for testing purposes
    # Or rely on the logic we added.
    
    # We can inject a dummy function into the proxy for this test
    step = Step([1])
    c = ColumnCollection(step, {"a": [1]})
    ops = CollectionOperations(c)
    
    def returns_scalar(col):
        return 42
    
    # Manually adding the method to the instance for testing
    setattr(ops, "returns_scalar", ops._create_operation_method(returns_scalar))
    
    result_ops = ops.returns_scalar()
    print(f"Scalar Result type: {type(result_ops)}")
    assert isinstance(result_ops, CollectionOperations)
    
    result_col = result_ops.end()
    assert "result" in result_col.columns
    assert result_col["result"].values[0] == 42
    assert result_col.step.values[0] == "returns_scalar"
    print("Scalar wrapping successful.")

if __name__ == "__main__":
    try:
        test_aggregation_chaining_dict()
        test_aggregation_chaining_scalar()
        print("\n\033[92mALL TESTS PASSED\033[0m")
    except Exception as e:
        print(f"\n\033[91mTEST FAILED: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
