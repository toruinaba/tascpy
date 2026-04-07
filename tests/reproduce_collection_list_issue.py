
import sys
import numpy as np
from tascpy.core.column import Column
from tascpy.core.collection import ColumnCollection
from tascpy.analytics.operations.list_proxy import CollectionListOperations

def create_mock_collection(name, val):
    return ColumnCollection(
        step=Column(None, "Step", None, [1, 2, 3]),
        columns={
            "Data": Column(None, "Data", "N", [val, val, val])
        },
        metadata={"name": name}
    )

def main():
    c1 = create_mock_collection("c1", 10.0)
    c2 = create_mock_collection("c2", 20.0)
    
    # Create CollectionListOperations
    clo = CollectionListOperations([c1, c2])
    
    print("Testing max(clo)...")
    try:
        # Instead of max(clo) which is ambiguous
        # We test clo.max("Data") which should now be supported via map
        # This returns a list of max values for each collection
        max_values = clo.max("Data")
        print("clo.max('Data') result:", max_values)
        if hasattr(max_values, "__iter__") and list(max_values) == [10.0, 20.0]:
            print("clo.max('Data') verification passed")
            # Verify type is list of floats, not CollectionOperations
            if isinstance(max_values, list) and isinstance(max_values[0], float):
                 print("clo.max('Data') type verification passed (List[float])")
            else:
                 print(f"clo.max('Data') type verification FAILED. Got {type(max_values)} containing {type(max_values[0]) if len(max_values)>0 else 'empty'}")

        else:
             print("clo.max('Data') verification FAILED")
             
    except Exception as e:
        print(f"clo.max('Data') failed: {e}")

    print("\nTesting clo.end()...")
    try:
        res = clo.end()
        print("clo.end() success")
    except AttributeError:
        print("clo.end() failed: AttributeError (expected)")
    except Exception as e:
        print(f"clo.end() failed: {e}")

if __name__ == "__main__":
    main()
