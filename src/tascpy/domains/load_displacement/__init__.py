"""tascpy.domains.load_displacement - 荷重-変位ドメイン"""

from .collection import LoadDisplacementCollection, as_load_displacement
from .ops import LoadDisplacementOps

__all__ = ["LoadDisplacementCollection", "LoadDisplacementOps", "as_load_displacement"]
