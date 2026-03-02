
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.core.column import Column

# Setup test collection
col = LoadDisplacementCollection(
    columns={
        "load": Column("ch1", "load", "kN", np.arange(10).tolist()),
        "disp": Column("ch2", "disp", "mm", np.arange(10).tolist()),
        "time": Column("ch3", "time", "s", np.arange(10).tolist())
    },
    displacement_column="disp",
    load_column="load",
    step=list(range(10))
)

print("1. Plot (plot_load_displacement)")
res_plot = col.ops.plot_load_displacement()
print(f"Result type: {type(res_plot)}")
if isinstance(res_plot, plt.Axes):
    print("Return Axes (chain breaks)")
elif isinstance(res_plot, LoadDisplacementCollection):
    print("Return Collection (chain continues) - EXPECTED TO FAIL CURRENTLY")
else:
    print(f"Unknown type: {type(res_plot)}")

print("\n2. Plot Skeleton (plot_skeleton_curve)")
# create dummy curve data first
col.metadata["curves"] = {"skeleton_curve": {"x": [0, 5, 10], "y": [0, 50, 100]}}
try:
    res_skel = col.ops.plot_skeleton_curve(plot_original=False)
    print(f"Result type: {type(res_skel)}")
except Exception as e:
    print(f"plot_skeleton_curve failed: {e}")

print("\n3. Plot Yield (plot_yield_point)")
# create dummy yield data
col.metadata["analysis"] = {
    "yield_point": {
        "method": "offset",
        "displacement": 2.0,
        "load": 20.0,
        "initial_slope": 10.0,
        "parameters": {"offset_value": 0.002, "range_start": 0.1, "range_end": 0.4}
    }
}
try:
    res_yield = col.ops.plot_yield_point(plot_original_data=False)
    print(f"Result type: {type(res_yield)}")
except Exception as e:
    print(f"plot_yield_point failed: {e}")
