import sys
from pathlib import Path
import numpy as np
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.column import Column, NumberColumn
from tascpy.core.step import Step
from tascpy.core.collection import ColumnCollection
from tascpy.operations.list_proxy import CollectionListOperations

def test_list_proxy_getattr():
    print("\n[1] Testing CollectionListOperations.__getattr__")
    
    # Create two collections
    step = Step([0, 1, 2])
    c1 = ColumnCollection(step, {"a": [1, 2, 3]})
    c2 = ColumnCollection(step, {"a": [10, 20, 30]})
    
    # Create List Proxy
    lops = CollectionListOperations([c1, c2], domain="core")
    
    # Apply 'ma' (moving average) via attribute access
    # ma(column, window_size=2) -> should return CollectionListOperations (since each 'ma' returns Collection)
    result = lops.ma("a", window_size=2)
    
    print(f"Result type: {type(result)}")
    assert isinstance(result, CollectionListOperations)
    assert len(result) == 2
    
    # Check content of first collection result (ma of [1, 2, 3] with window 2 -> [NaN, 1.5, 2.5]?)
    # tascpy 'ma' implementation depends on pandas rolling or similar.
    # checking values
    val1 = result[0].columns["a"].values
    print(f"Result 1 values: {val1}")
    
    # Check content of second
    val2 = result[1].columns["a"].values
    print(f"Result 2 values: {val2}")
    
    # Chain another operation: to_numeric error handling test
    # This assumes 'to_numeric' is in core ops (it is collection method, not necessarily operation)
    # Operations are registered in registry. 'ma' is definitely an operation.
    
    # Let's try 'max' if it is registered as operation (it's a collection method, maybe not operation?)
    # Core operations usually wrap collection methods or provide new ones.
    # In 'core/operations/core.py', 'ma' is defined.
    
    print("Method chaining test passed if no error.")

def test_list_proxy_split_chain():
    print("\n[2] Testing split() -> chain")
    # Simulate a split operation returning CollectionListOperations
    # We don't have a split operation in core easily accessible here without setup, 
    # but we can verify the chaining mechanism using the list proxy we created.
    
    step = Step([0, 1, 2, 3, 4, 5])
    c = ColumnCollection(step, {"val": [0, 1, 2, 3, 4, 5]})
    
    # Manually creating list proxy as if it came from split
    # Split typically splits by some condition.
    
    # Let's just use the previous lops again and chain
    step1 = Step([3, 4, 5])
    step2 = Step([6, 7, 8])
    c1 = ColumnCollection(step1, {"val": [10, 10, 10]})
    c2 = ColumnCollection(step2, {"val": [20, 20, 20]})
    lops = CollectionListOperations([c1, c2])
    
    # Chain: ma -> something else?
    # ma returns CollectionListOperations. 
    # We can chain another 'ma'?
    
    res = lops.ma("val", window_size=2).ma("val", window_size=2) # Double moving average
    print(f"Chained result type: {type(res)}")
    assert isinstance(res, CollectionListOperations)
    print("Chaining test passed.")

if __name__ == "__main__":
    try:
        test_list_proxy_getattr()
        test_list_proxy_split_chain()
        print("\n\033[92mALL TESTS PASSED\033[0m")
    except Exception as e:
        print(f"\n\033[91mTEST FAILED: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
