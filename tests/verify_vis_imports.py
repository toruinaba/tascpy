import matplotlib.pyplot as plt
from tascpy.operations.strain.visualization import plot_rosette_vectors
# Mock StrainCollection and plotting
try:
    # Basic import success
    print("Visualization module import success")
except ImportError as e:
    print(f"Visualization module import failed: {e}")
