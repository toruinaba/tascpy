from .data_holder import DataHolder
from typing import Any, Optional, Union


class Step(DataHolder):
    """インデックス列を表す専用クラス"""

    def __init__(self, values=None, metadata=None):
        super().__init__("Step", values, metadata)
        self.validate()

    def clone(self):
        from copy import deepcopy

        return Step(deepcopy(self.values))

    def validate(self):
        """データ有効性チェック"""
        pass

    def find_step_index(
        self, value: Any, tolerance: Optional[float] = None, default: Any = None
    ) -> Union[int, Any]:
        """値を検索してインデックスを返却する

        指定された値に一致するデータのインデックスを返します。
        tolerance が指定された場合は、指定された許容範囲内の値も一致とみなします。

        Args:
            value: 検索する値
            tolerance: 許容範囲（デフォルトはNone）
            default: 値が見つからない場合に返す値（デフォルトはNone）

        Returns:
            int: 見つかった場合はインデックス
            Any: 見つからない場合はdefaultの値

        Examples:
            >>> step = Step(values=[1.0, 2.0, 3.0, 4.0, 5.0])
            >>> step.find_step_index(3.0)
            2
            >>> step.find_step_index(3.1, tolerance=0.2)
            2
            >>> step.find_step_index(6.0, default=-1)
            -1
        """
        if not self.values:
            return default

        if tolerance is not None:
            # 許容範囲内の値を検索
            for i, val in enumerate(self.values):
                if val is not None and (value - tolerance) <= val <= (value + tolerance):
                    return i
        else:
            # 完全一致の値を検索
            try:
                return self.values.index(value)
            except ValueError:
                pass

        # 値が見つからない場合
        return default
