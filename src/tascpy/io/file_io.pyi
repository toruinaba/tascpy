from typing import Union, TextIO, List, Any, Optional
from pathlib import Path
from tascpy.core.collection import ColumnCollection

def load_collection(
    filepath_or_stream: Union[str, Path, TextIO],
    format_name: str = ...,
    auto_detect_types: bool = ...,
    collection_cls: Optional[Any] = ...,
    **kwargs: Any
) -> ColumnCollection: ...
