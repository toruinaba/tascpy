from typing import Any, List, Dict, Tuple, Union, Callable

from .channel import Channel
from .base_data_container import (
    PlottingMixin,
    DataExtractionMixin,
    DataSplitMixin,
    IOHandlerMixin,
    BaseDataContainer
)

class ChannelGroup(
        PlottingMixin,
        DataExtractionMixin,
        DataSplitMixin,
        IOHandlerMixin,
        BaseDataContainer
    ):
    """複数のチャンネルをまとめるクラス
    """

    def __init__(
        self,
        chs: List[str],
        names: List[str],
        units: List[str],
        steps: List[int],
        data: Dict[str, Channel]
    ):
        self.chs = chs
        self.names = names
        self.units = units
        self.steps = steps
        self.dict = data

    def __getitem__(self, item) -> Channel:
        return super().__getitem__(item)
