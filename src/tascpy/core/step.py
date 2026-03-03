from .data_holder import DataHolder
from typing import Any, Optional, Union
import numpy as np


class Step(DataHolder):
    """インデックス列を表す専用クラス
    
    Examples:
        >>> from tascpy.core.step import Step
        >>> step = Step(values=[0.0, 1.0, 2.0])
        >>> step.find_nearest_index(1.2)
        1
    """

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
        
        Examples:
            >>> from tascpy.core.step import Step
            >>> step = Step(values=[0.0, 1.0, 2.0])
            >>> step.find_step_index(1.0)
            1
        """
        if len(self.values) == 0:
            return default

        # NumPy配列での検索
        
        if tolerance is not None:
             # 許容範囲内での検索
             # np.isclose は全要素チェックになるので遅い可能性があるが、ループよりは早い
             # 公差がある場合は where で条件に合う最初のインデックスを探す
             
             from tascpy.analytics.functional.filters import find_index_with_tolerance
             return find_index_with_tolerance(self.values, value, tolerance, default)
                 
        else:
             # 完全一致
             # np.where で検索
             indices = np.where(self.values == value)[0]
             if len(indices) > 0:
                 return int(indices[0])

        # 値が見つからない場合
        return default

    def find_nearest_index(self, value: Any) -> int:
        """指定した値に最も近い要素のインデックスを返す
        
        Args:
            value: 検索する値
            
        Returns:
            int: 最も近い要素のインデックス。配列が空の場合は-1
            
        Examples:
            >>> from tascpy.core.step import Step
            >>> step = Step(values=[0.0, 10.0, 20.0])
            >>> step.find_nearest_index(12.0)
            1
        """
        if len(self.values) == 0:
            return -1
            
        if isinstance(self.values, np.ndarray) and np.issubdtype(self.values.dtype, np.number):
            # 数値配列の場合、絶対差の最小値のインデックスを返す
            idx = (np.abs(self.values - value)).argmin()
            return int(idx)
        else:
            # それ以外（リストなど）の場合は、差を計算できると仮定して処理
            # 数値でない場合はエラーになる可能性があるが、Stepは通常数値を想定
            try:
                # リストの場合
                values_arr = np.array(self.values)
                if np.issubdtype(values_arr.dtype, np.number):
                     idx = (np.abs(values_arr - value)).argmin()
                     return int(idx)
                else:
                     # 数値として扱えないデータが含まれる場合、単純な比較は難しい
                     # ここでは例外を発生させるか、最初の要素を返す等の対応が必要だが
                     # Stepクラスの性質上、数値であることを期待してエラーを投げる
                     raise TypeError("Step values must be numeric to find nearest index")
            except Exception:
                raise TypeError("Step values must be numeric to find nearest index")
