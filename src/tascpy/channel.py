from typing import Any, List, Dict, Union
from dataclasses import dataclass, asdict


@dataclass
class Channel:
    """チャンネルデータ単一格納クラス

    チャンネルデータ(タスクの列)を格納するデータクラス.
    """

    ch: str
    """チャンネル"""
    name: str
    """名前"""
    unit: str
    """単位"""
    steps: List[int]
    """ステップ"""
    data: List[Union[float, bool, None]]
    """データ"""

    def __getitem__(self, i) -> Union[float, bool, None]:
        return self.data[i]

    @property
    def removed_data(self) -> List[Union[float, bool]]:
        """Noneを除くデータ"""
        return [x for x in self.data if x is not None]

    @property
    def removed_step(self) -> List[int]:
        """Noneのデータを除くステップ"""
        return [
            self.steps[x] for x in range(len(self.data)) if self.data[x] is not None
        ]

    @property
    def max(self) -> float:
        """最大値"""
        return max(self.removed_data)

    @property
    def maxrow(self) -> int:
        """最大値インデックス"""
        return self.data.index(self.max)

    @property
    def maxstep(self) -> int:
        """最大値ステップ"""
        return self.maxrow + 1

    @property
    def min(self) -> float:
        """最小値"""
        return min(self.removed_data)

    @property
    def minrow(self) -> int:
        """最小値インデックス"""
        return self.data.index(self.min)

    @property
    def minstep(self) -> int:
        """最小値ステップ"""
        return self.minrow + 1

    @property
    def absmax(self) -> float:
        """絶対値最大"""
        abs_list = [abs(x) for x in self.removed_data]
        return max(abs_list)

    @property
    def absmin(self) -> float:
        """絶対値最小"""
        return min([abs(x) for x in self.removed_data])

    def fetch_near_step(
        self, value, method=0, maxstep=None
    ) -> int:
        """値検索関数
        引数に対して一番近い値を検索.
        method=0の場合は距離絶対値最小
        method=1は指定値以下の距離絶対値最小
        method=2は指定値以上の距離絶対値最小
        """
        if maxstep:
            obj_data = [x for x in self.data[:maxstep - 1] if x is not None]
        else:
            obj_data = [x for x in self.data if x is not None]
        if method == 0:
            distances = [abs(x - value) for x in obj_data]
        elif method == 1:
            distances = [abs(x - value) for x in obj_data if x - value < 0]
        elif method == 2:
            distances = [abs(x - value) for x in obj_data if x - value < 0]
        near_value = obj_data[distances.index(min(distances))]
        return self.data.index(near_value) + 1

    def extract_data(self, steps: List[int]):
        """対象ステップのデータ抽出
        """
        idxs = [self.steps.index(x) for x in steps]
        extracted = [self.data[x] for x in idxs]
        return Channel(self.ch, self.name, self.unit, steps, extracted)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
