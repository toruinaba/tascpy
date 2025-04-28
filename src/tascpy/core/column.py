from .data_holder import DataHolder


class Column(DataHolder):
    """データ列を表すクラス"""

    def __init__(self, ch, name, unit, values=None, metadata=None):
        super().__init__(name, values, metadata)
        self.ch = ch
        self.unit = unit

    def clone(self):
        from copy import deepcopy

        return Column(self.ch, self.name, self.unit, deepcopy(self.values))
