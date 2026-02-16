from typing import Any, List, Dict, Optional, Union
import numpy as np
from ...core.collection import ColumnCollection
from ..registry import operation, register_functional
from ..abstraction import split_result, inject_length
from ...functional import split as functional_split


split_by_integers = register_functional(
    functional_split.split_by_integers,
    domain="core",
    name="split_by_integers",
    extra_decorators=[inject_length, split_result],
    signature_override={
        "length": ("length", int),
        "markers": ("markers", List[int])
    }
)


split_at_indices = register_functional(
    functional_split.split_at_indices,
    domain="core",
    name="split_at_indices",
    extra_decorators=[inject_length, split_result],
    signature_override={
        "length": ("length", int),
        "indices": ("indices", Union[int, List[int]])
    }
)

