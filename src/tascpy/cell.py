from typing import Any, Dict, Union
from dataclasses import dataclass, asdict


@dataclass
class Cell:
    """単一データ格納クラス
    """
    ch: str
    """チャンネル"""
    name: str
    """名前"""
    unit: str
    """単位"""
    step: int
    """ステップ"""
    data: Union[float, bool, None]
    """計測データ"""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
