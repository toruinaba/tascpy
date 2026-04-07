from pathlib import Path
from typing import Union, Any
from tascpy.core.collection import ColumnCollection

def load_from_file(
    file_path: Union[str, Path],
    format_name: str = ...,
    **kwargs: Any
) -> ColumnCollection: ...

def save_to_file(
    collection: ColumnCollection,
    file_path: Union[str, Path],
    format_name: str = ...,
    **kwargs: Any
) -> None: ...

def load_tasc_file(
    file_path: Union[str, Path],
    **kwargs: Any
) -> ColumnCollection: ...
