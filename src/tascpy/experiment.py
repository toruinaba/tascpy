from typing import Any, List, Dict, Tuple, Union

from .channel import Channel
from .base_data_container import (
    PlottingMixin,
    DataExtractionMixin,
    IOHandlerMixin,
    BaseDataContainer
)

class Experiment(
        PlottingMixin,
        DataExtractionMixin,
        IOHandlerMixin,
        BaseDataContainer
    ):
    """全計測結果格納クラス
    """

    def __init__(
        self,
        title: str,
        chs: List[str],
        names: List[str],
        units: List[str],
        steps: List[int],
        date: List[str],
        time: List[str],
        data: Dict[str, Channel]
    ):
        """初期化関数"""
        self.title = title
        self.chs = chs
        self.names = names
        self.units = units
        self.steps = steps
        self.date = date
        self.time = time
        self.dict = data

    def __getitem__(self, item) -> Channel:
        return super().__getitem__(item)
