class DataHolder:
    """データ値とメタデータを保持する基本クラス"""

    def __init__(self, name, values=None, metadata=None):
        self.name = name
        self.values = values if values is not None else []
        self.metadata = metadata if metadata is not None else {}

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def clone(self):
        NotImplementedError

    def apply(self, func, *args, **kwargs):
        """関数を適用して新しいSeriesを作成"""
        new_series = self.clone()
        new_series.values = func(self.values, *args, **kwargs)
        return new_series
