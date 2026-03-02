import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
import matplotlib.pyplot as plt

# Create dummy collection
col = ColumnCollection(
    step=list(range(10)),
    columns={
        "x": Column("x", "x", "", np.arange(10).tolist()),
        "y": Column("y", "y", "", (np.arange(10)**2).tolist())
    }
)

# Test plotting (should not error)
try:
    # Use non-blocking show for test
    plt.show = lambda: None
    col.ops.plot("x", "y")
    print("Core plot verification: Success")
except Exception as e:
    print(f"Core plot verification: Failed - {e}")
    raise
