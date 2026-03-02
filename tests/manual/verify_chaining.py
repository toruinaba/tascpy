import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column

# Setup test collection
col = ColumnCollection(
    columns={
        "data": Column("ch1", "data", "unit", np.arange(10).tolist()),
        "time": Column("ch2", "time", "s", np.arange(10).tolist())
    },
    step=list(range(10))
)

res_max = col.ops.max("data")
print(f"Result type: {type(res_max)}")
if isinstance(res_max, ColumnCollection):
    print("Wrapped in Collection")
elif isinstance(res_max, (dict, float, int, np.floating, np.integer)):
    print("Raw value/dict")

print("\n2. Plot (plot)")
res_plot = col.ops.plot()
print(f"Result: {res_plot}")
print(f"Result type: {type(res_plot)}")
if isinstance(res_plot, ColumnCollection):
    print("Wrapped in Collection (chain continues)")
else:
    print("Return value (chain breaks)")

print("\n3. Plotly (iplot)")
try:
    res_iplot = col.ops.iplot(x_column="time", y_column="data")
    print(f"Result type: {type(res_iplot)}")
    if isinstance(res_iplot, ColumnCollection):
        print("Wrapped in Collection (chain continues)")
    elif isinstance(res_iplot, go.Figure):
        print("Return Figure (chain breaks/changes)")
except Exception as e:
    print(f"iplot failed: {e}")

print("\n4. Export (not implemented yet, but conceptually similar)")
pass
