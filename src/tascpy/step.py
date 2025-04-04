from typing import Any, List, Dict, Union
from dataclasses import dataclass
    
from .cell import Cell
from .plot_utils import plot_helper

@dataclass
class Step:
    """単一ステップ格納クラス
    """
    def __init__(self, chs, names, units, step, row):
        self.chs = chs
        self.names = names
        self.dict = {
            x: Cell(x, y, z, step, w)
            for x, y, z, w in zip(chs, names, units, row)
        }

    def __getitem__(self, item) -> Cell:
        if item in self.names:
            ch = self.chs[self.names.index(item)]
            return self.dict[ch]
        else:
            return self.dict[item]

    def __repr__(self) -> str:
        return str(self.dict)

    def plot_const_x(
        self,
        x: List[float],
        y: Union[List[str], List[List[str]]],
        ax=None,
        **kwargs
    ):
        if isinstance(y[0], str):
            y_val = [self[name].data for name in y]
            return plot_helper(x, y_val, ax=ax, **kwargs)
        elif isinstance(y[0], list):
            result = None
            for names in y:
                y_val = [self[name].data for name in names]
                result = plot_helper(x, y_val, ax=ax, **kwargs)
            return result

    def plot_const_y(
        self,
        y: List[float],
        x: Union[List[str], List[List[str]]],
        ax=None,
        **kwargs
    ):
        if isinstance(x[0], str):
            x_val = [self[name].data for name in x]
            return plot_helper(x_val, y, ax=ax, **kwargs)
        elif isinstance(x[0], list):
            result = None
            for names in x:
                x_val = [self[name].data for name in names]
                result = plot_helper(x_val, y, ax=ax, **kwargs)
            return result

    def to_dict(self) -> Dict[str, Any]:
        rtn_dict = {k: v.to_dict() for k, v in self.dict.items()}
        return rtn_dict
