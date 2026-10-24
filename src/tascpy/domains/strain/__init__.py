"""tascpy.domains.strain - ひずみドメイン"""

from .collection import StrainCollection, as_strain
from .ops import StrainOps

__all__ = ["StrainCollection", "StrainOps", "as_strain"]
