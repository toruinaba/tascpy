import numpy as np

class DataHolder:
    """データ値とメタデータを保持する基本クラス"""

    def __init__(self, name, values=None, metadata=None):
        self.name = name
        # NumPy配列として保持 (デフォルトは空の配列)
        if values is None:
            self.values = np.array([])
        elif isinstance(values, np.ndarray):
            self.values = values
        else:
            try:
                self.values = np.array(values)
            except ValueError:
                # 形状が不揃いな配列（シーケンスを含む）や型が混在する場合
                self.values = np.array(values, dtype=object)
            
        self.metadata = metadata if metadata is not None else {}

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def __repr__(self) -> str:
        name = self.name if self.name else "Unnamed"
        size = len(self)
        if size == 0:
            preview = "[]"
        else:
            try:
                vals = list(self.values)
                if size <= 6:
                    preview = f"{vals}"
                else:
                    preview = f"[{vals[0]}, {vals[1]}, ..., {vals[-2]}, {vals[-1]}]"
            except Exception:
                preview = "[...]"
        return f"<{self.__class__.__name__} name='{name}' length={size} values={preview}>"

    def clone(self):
        NotImplementedError

    def apply(self, func, *args, **kwargs):
        """関数を適用して新しいSeriesを作成"""
        new_series = self.clone()
        new_series.values = func(self.values, *args, **kwargs)
        return new_series
