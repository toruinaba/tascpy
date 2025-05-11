from .data_holder import DataHolder


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
