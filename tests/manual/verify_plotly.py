import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column

# Create dummy collection
col = ColumnCollection(
    step=list(range(10)),
    columns={
        "x": Column("x", "x", "", np.arange(10).tolist()),
        "y": Column("y", "y", "", (np.arange(10)**2).tolist())
    }
)


# Test iplot (should return a Figure object, or error if plotly missing)
try:
    fig = col.ops.iplot("x", "y")
    print(f"iplot verification: Success (Returned type: {type(fig)})")
    
    # Check if it has data
    if hasattr(fig, "data") and len(fig.data) > 0:
        print("Figure has data.")
    else:
        print("Figure has NO data.")
        
except ImportError:
    print("iplot verification: Skipped (Plotly not installed)")
except Exception as e:
    print(f"iplot verification: Failed - {e}")
    raise
