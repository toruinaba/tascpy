import sys
from pathlib import Path
import pytest
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.column import Column
from tascpy.core.step import Step
from tascpy.core.collection import ColumnCollection
from tascpy.operations.list_proxy import CollectionListOperations

def test_list_aggregation_chain():
    print("\n[1] Testing split() -> max() chain")
    
    # Simulate valid split result (List of Collections)
    # Col 1: [1, 2, 3] -> max 3
    # Col 2: [10, 20, 30] -> max 30
    step1 = Step([1, 2, 3])
    c1 = ColumnCollection(step1, {"val": [1, 2, 3]})
    
    step2 = Step([4, 5, 6])
    c2 = ColumnCollection(step2, {"val": [10, 20, 30]})
    
    # Create List Proxy
    lops = CollectionListOperations([c1, c2], domain="core")
    
    # Apply 'max' via attribute access (chained)
    # Should apply max to each collection -> returns CollectionListOperations of 1-row collections
    result_lops = lops.max()
    
    print(f"Result type: {type(result_lops)}")
    assert isinstance(result_lops, CollectionListOperations)
    assert len(result_lops) == 2
    
    # Check first result
    res1 = result_lops[0] # Returns CollectionOperations
    col1 = res1.end()
    print(f"Result 1 columns: {col1.columns.keys()}")
    print(f"Result 1 step: {col1.step.values}")
    print(f"Result 1 val: {col1['val'].values}")
    
    assert col1.step.values[0] == "max"
    assert col1['val'].values[0] == 3
    
    # Check second result
    res2 = result_lops[1].end()
    print(f"Result 2 val: {res2['val'].values}")
    assert res2['val'].values[0] == 30
    
    print("List aggregation chaining successful.")
    
    # Test further chaining
    # .max() -> CollectionListOperations -> .to_numeric() (map)
    chained = lops.max().to_numeric()
    assert isinstance(chained, CollectionListOperations)
    print("Further chaining successful.")

if __name__ == "__main__":
    try:
        test_list_aggregation_chain()
        print("\n\033[92mALL TESTS PASSED\033[0m")
    except Exception as e:
        print(f"\n\033[91mTEST FAILED: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
