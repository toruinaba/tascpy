from typing import Any, List, Dict, Union
from dataclasses import dataclass\
    
from .cell import Cell

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
        if ax:
            if isinstance(y[0], str):
                y_val = [self[name].data for name in y]
                ax.plot(x, y_val, **kwargs)
            elif isinstance(y[0], list):
                for names in y:
                    y_val = [self[name].data for name in names]
                    ax.plot(x, y_val, **kwargs)
            return ax
        else:
            from matplotlib import pyplot as plt
            fig = plt.figure()
            if isinstance(y[0], str):
                y_val = [self[name].data for name in y]
                plt.plot(x, y_val, **kwargs)
            elif isinstance(y[0], list):
                for names in y:
                    y_val = [self[name].data for name in names]
                    plt.plot(x, y_val, **kwargs)

    def plot_const_y(
        self,
        y: List[float],
        x: Union[List[str], List[List[str]]],
        ax=None,
        **kwargs
    ):
        if ax:
            if isinstance(x[0], str):
                x_val = [self[name].data for name in x]
                ax.plot(x_val, y, **kwargs)
            elif isinstance(x[0], list):
                for names in x:
                    x_val = [self[name].data for name in names]
                    ax.plot(x_val, y, **kwargs)
            return ax
        else:
            from matplotlib import pyplot as plt
            fig = plt.figure()
            if isinstance(x[0], str):
                x_val = [self[name].data for name in x]
                plt.plot(x_val, y, **kwargs)
            elif isinstance(x[0], list):
                for names in x:
                    x_val = [self[name].data for name in names]
                    plt.plot(x_val, y, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        rtn_dict = {k: v.to_dict() for k, v in self.dict.items()}
        return rtn_dict