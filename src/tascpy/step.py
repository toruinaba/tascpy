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

    def _plot_common(
        self,
        const_values: List[float],
        names: Union[List[str], List[List[str]]],
        is_x_const: bool,
        ax=None,
        **kwargs
    ):
        """共通プロット関数
        
        Args:
            const_values: 固定軸の値リスト
            names: 可変軸の名前リスト
            is_x_const: X軸が固定かどうか
            ax: プロット先の軸
            **kwargs: plot_helperに渡す追加引数
            
        Returns:
            プロット結果
        """
        if isinstance(names[0], str):
            var_values = [self[name].data for name in names]
            if is_x_const:
                return plot_helper(const_values, var_values, ax=ax, **kwargs)
            else:
                return plot_helper(var_values, const_values, ax=ax, **kwargs)
        elif isinstance(names[0], list):
            result = None
            for name_list in names:
                var_values = [self[name].data for name in name_list]
                if is_x_const:
                    result = plot_helper(const_values, var_values, ax=ax, **kwargs)
                else:
                    result = plot_helper(var_values, const_values, ax=ax, **kwargs)
            return result

    def plot_const_x(
        self,
        x: List[float],
        y: Union[List[str], List[List[str]]],
        ax=None,
        **kwargs
    ):
        """X軸固定プロット
        
        Args:
            x: X軸の値リスト
            y: Y軸の名前リスト
            ax: プロット先の軸
            **kwargs: plot_helperに渡す追加引数
            
        Returns:
            プロット結果
        """
        return self._plot_common(x, y, is_x_const=True, ax=ax, **kwargs)

    def plot_const_y(
        self,
        y: List[float],
        x: Union[List[str], List[List[str]]],
        ax=None,
        **kwargs
    ):
        """Y軸固定プロット
        
        Args:
            y: Y軸の値リスト
            x: X軸の名前リスト
            ax: プロット先の軸
            **kwargs: plot_helperに渡す追加引数
            
        Returns:
            プロット結果
        """
        return self._plot_common(y, x, is_x_const=False, ax=ax, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        rtn_dict = {k: v.to_dict() for k, v in self.dict.items()}
        return rtn_dict
