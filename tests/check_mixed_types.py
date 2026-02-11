import sys
from pathlib import Path
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tascpy.core.column import Column, NumberColumn, StringColumn, InvalidColumn, detect_column_type

def check_mixed_types():
    print("Checking Mixed Type Handling...")

    # Case 1: Numbers with None
    data1 = [1.0, 2.0, None, 4.0]
    col1 = detect_column_type(None, "col1", None, data1)
    print(f"\n[Case 1] [1.0, 2.0, None, 4.0]")
    print(f"Type: {type(col1).__name__}")
    print(f"Values: {col1.values}")
    print(f"Dtype: {col1.values.dtype if hasattr(col1.values, 'dtype') else 'list'}")

    # Case 2: Numbers with String (that cannot be float)
    data2 = [1.0, 2.0, "error", 4.0]
    col2 = detect_column_type(None, "col2", None, data2)
    print(f"\n[Case 2] [1.0, 2.0, 'error', 4.0]")
    print(f"Type: {type(col2).__name__}")
    print(f"Values: {col2.values}")
    print(f"Dtype: {col2.values.dtype if hasattr(col2.values, 'dtype') else 'list'}")

    # Case 3: Numbers with String (that CAN be float)
    data3 = [1.0, 2.0, "3.0", 4.0]
    col3 = detect_column_type(None, "col3", None, data3)
    print(f"\n[Case 3] [1.0, 2.0, '3.0', 4.0]")
    print(f"Type: {type(col3).__name__}")
    print(f"Values: {col3.values}")
    
    # Case 4: Explicit NumberColumn with invalid string
    print(f"\n[Case 4] Explicit NumberColumn with [1.0, 'error']")
    try:
        col4 = NumberColumn(None, "col4", None, [1.0, "error"])
        print(f"Created: {col4.values}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_mixed_types()
