import numpy as np
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.domains.strain import StrainCollection
from tascpy.core.column import Column
import tascpy.analytics.operations # Force load

# 1. Verify LoadDisplacement iplot
print("Verifying LoadDisplacement iplot...")
ld_col = LoadDisplacementCollection(
    step=list(range(10)),
    columns={
        "load": Column("ch1", "load", "kN", np.arange(10).tolist()),
        "disp": Column("ch2", "disp", "mm", (np.arange(10)*2).tolist())
    },
    displacement_column="disp"
)
try:
    fig = ld_col.ops.iplot_load_displacement()
    print(f"iplot_load_displacement success: {type(fig)}")
    
    # Check skeleton curve iplot (mocking data)
    ld_col.columns["skeleton_curve_x"] = Column("calc", "skeleton_curve_x", "", [0, 10, 20])
    ld_col.columns["skeleton_curve_y"] = Column("calc", "skeleton_curve_y", "", [0, 5, 8])
    # manually set metadata for get_curve_data fallback if needed, or if function relies on specific structure
    # The refactored function looks for metadata or specific column names.
    # We'll skip deep verification of curve data retrieval logic here, focusing on function existence.
    fig = ld_col.ops.iplot_skeleton_curve()
    print(f"iplot_skeleton_curve success: {type(fig)}")

except Exception as e:
    print(f"LoadDisplacement iplot failed: {e}")
    # raise e

# 2. Verify Strain iplot
print("\nVerifying Strain iplot...")
strain_col = StrainCollection(
    step=list(range(1)),
    columns={
        "R1_e1": Column("ch1", "R1_e1", "u", [1000]),
        "R1_e2": Column("ch2", "R1_e2", "u", [-500]),
        "R1_theta": Column("calc", "R1_theta", "deg", [30])
    }
)
# Add rosette metadata and layout
strain_col.add_rosette("R1", {"columns": ["R1_e1", "R1_e2", "R1_theta"]}) # simplified
strain_col.set_column_coordinates("R1_e1", 10, 20, 0)

try:
    fig = strain_col.ops.iplot_rosette_vectors("R1")
    print(f"iplot_rosette_vectors success: {type(fig)}")
except Exception as e:
    print(f"Strain iplot failed: {e}")
    raise e
