from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Row:
    """ColumnCollectionの1行を表現するクラス"""

    step: Any
    values: Dict[str, Any]

    def __repr__(self) -> str:
        vals = {k: self.values[k] for k in list(self.values.keys())[:3]}
        if len(self.values) > 3:
            vals["..."] = "..."
        return f"<Row step={self.step} values={vals}>"

    def __getitem__(self, key: str) -> Any:
        """列名による値へのアクセス"""
        if key == "step":
            return self.step
        if key in self.values:
            return self.values[key]
        raise KeyError(f"列'{key}'が存在しません")

    def __iter__(self):
        """値の反復処理"""
        yield "step", self.step
        yield from self.values.items()

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {"step": self.step, **self.values}
