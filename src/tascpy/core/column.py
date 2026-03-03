from .data_holder import DataHolder
from typing import List, Any, Optional, Dict, Union, Type
from copy import deepcopy
import numpy as np


class Column(DataHolder):
    """データ列を表すクラス"""

    def __init__(self, ch, name, unit, values=None, metadata=None):
        super().__init__(name, values, metadata)
        self.ch = ch
        self.unit = unit

    def __repr__(self) -> str:
        name = str(self.name) if self.name else "Unnamed"
        unit_str = f" unit='{self.unit}'" if self.unit else ""
        ch_str = f" ch='{self.ch}'" if self.ch else ""
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
        return f"<{self.__class__.__name__}{ch_str} name='{name}'{unit_str} length={size} values={preview}>"

    def clone(self):
        from copy import deepcopy

        return Column(
            self.ch,
            self.name,
            self.unit,
            deepcopy(self.values),
            deepcopy(self.metadata),
        )

    def count_nones(self) -> int:
        """None値の数をカウント
        
        Note:
            内部的にはNaNをNoneとして扱います（数値カラムの場合）
        """
        if len(self.values) == 0:
            return 0
            
        # オブジェクト配列(Noneを含む)の場合
        if self.values.dtype == object:
            return sum(1 for v in self.values if v is None)
        
        # 数値配列(NaNを含む)の場合
        if np.issubdtype(self.values.dtype, np.number):
            return np.isnan(self.values).sum()
            
        return 0

    def none_indices(self) -> List[int]:
        """None値を持つインデックスのリストを返す"""
        if len(self.values) == 0:
            return []
            
        if self.values.dtype == object:
             return [i for i, v in enumerate(self.values) if v is None]
        
        if np.issubdtype(self.values.dtype, np.number):
             return np.where(np.isnan(self.values))[0].tolist()

        return []

    def has_none(self) -> bool:
        """None値が1つ以上あるかどうかを返す"""
        if len(self.values) == 0:
            return False
            
        if self.values.dtype == object:
            return any(v is None for v in self.values)
            
        if np.issubdtype(self.values.dtype, np.number):
            return np.isnan(self.values).any()
            
        return False

    def _get_non_none_values(self) -> np.ndarray:
        """None以外の値のリスト(配列)を返す"""
        if len(self.values) == 0:
             return np.array([])
             
        if self.values.dtype == object:
             return np.array([v for v in self.values if v is not None])
             
        if np.issubdtype(self.values.dtype, np.number):
             return self.values[~np.isnan(self.values)]
             
        return self.values

    def max(self) -> Optional[Any]:
        """最大値を取得

        Returns:
            Any: データの最大値
            None: データがない場合はNone
        """
        non_none_values = self._get_non_none_values()
        if len(non_none_values) == 0:
            return None
        try:
            return max(non_none_values)
        except (TypeError, ValueError):
            # 比較できない型のデータが含まれる場合
            return None

    def min(self) -> Optional[Any]:
        """最小値を取得

        Returns:
            Any: データの最小値
            None: データがない場合はNone
        """
        non_none_values = self._get_non_none_values()
        if len(non_none_values) == 0:
            return None
        try:
            return min(non_none_values)
        except (TypeError, ValueError):
            # 比較できない型のデータが含まれる場合
            return None

    @property
    def max_index(self) -> Optional[int]:
        """最大値のインデックスを取得"""
        if len(self.values) == 0:
            return None
            
        values = self.values
        # NumPy配列かつ数値型の場合
        if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
            # NaNを無視して最大値のインデックスを取得
            try:
                # nanargmaxは全てNaNの場合にValueError
                if np.isnan(values).all():
                    return None
                return int(np.nanargmax(values))
            except ValueError:
                return None
        else:
            # リストやオブジェクト配列の場合
            try:
                # Noneを除外して最大値を探す
                valid_indices = [i for i, v in enumerate(values) if v is not None]
                if not valid_indices:
                    return None
                
                # 最大値を持つインデックスを返す
                # 同じ値が複数ある場合は最初のインデックス
                
                # 型が混在するとmax()でエラーになる可能性があるためループで処理
                valid_values = [values[i] for i in valid_indices]
                if not valid_values:
                    return None
                    
                max_v = max(valid_values)
                # 元のインデックスを探す
                for i in valid_indices:
                    if values[i] == max_v:
                        return i
                return None
            except (TypeError, ValueError):
                return None

    def mean(self) -> Optional[float]:
        """平均値を取得

        Returns:
            float: 数値データの平均値
            None: データがない場合や数値以外の場合はNone
        """
        return None

    def median(self) -> Optional[float]:
        """中央値を取得

        Returns:
            float: 数値データの中央値
            None: データがない場合や数値以外の場合はNone
        """
        return None

    def std(self) -> Optional[float]:
        """標準偏差を取得

        Returns:
            float: 数値データの標準偏差
            None: データが1つ以下の場合や数値以外の場合はNone
        """
        return None

    def sum(self) -> Optional[float]:
        """合計値を取得

        Returns:
            float: 数値データの合計
            None: データがない場合や数値以外の場合はNone
            0: 計算可能だが合計が0の場合
        """
        return None

    def variance(self) -> Optional[float]:
        """分散を取得

        Returns:
            float: 数値データの分散
            None: データが1つ以下の場合や数値以外の場合はNone
        """
        return None

    def quantile(self, q: float) -> Optional[Any]:
        """指定したパーセンタイルの値を取得

        Args:
            q: 0から1の間の割合（パーセンタイル値）

        Returns:
            Any: 指定したパーセンタイルの値
            None: データがない場合や計算できない場合はNone

        Raises:
            ValueError: qが0から1の範囲外の場合
        """
        return None


    def ptp(self) -> Optional[Any]:
        """最大値と最小値の差 (Peak to Peak) を取得
        
        Returns:
            Any: 最大値 - 最小値
            None: 計算不能な場合
        """
        try:
            max_val = self.max()
            min_val = self.min()
            if max_val is None or min_val is None:
                return None
            return max_val - min_val
        except (TypeError, ValueError):
            return None

    def abs_max(self) -> Optional[Any]:
        """絶対値の最大値を取得
        
        Returns:
            Any: 絶対値の最大値
            None: 計算不能な場合
        """
        non_none = self._get_non_none_values()
        if len(non_none) == 0:
            return None
        try:
            # np.abs が使える場合（数値配列）
            if isinstance(non_none, np.ndarray) and np.issubdtype(non_none.dtype, np.number):
                return np.max(np.abs(non_none))
            # そうでない場合
            return max(abs(v) for v in non_none)
        except (TypeError, ValueError):
            return None

    @property
    def n_valid(self) -> int:
        """有効なデータ数（None/NaN以外）を取得"""
        return len(self) - self.count_nones()

    def is_valid(self) -> np.ndarray:
        """各要素が有効かどうか（None/NaNでないか）のブール値配列を返す"""
        if len(self.values) == 0:
            return np.array([], dtype=bool)
            
        if self.values.dtype == object:
            return np.array([v is not None for v in self.values], dtype=bool)
            
        if np.issubdtype(self.values.dtype, np.number):
            return ~np.isnan(self.values)
            
        # その他の場合（文字列など）、NoneでなければTrue
        return np.array([v is not None for v in self.values], dtype=bool)

    @property
    def first_valid_index(self) -> Optional[int]:
        """最初の有効な値のインデックスを取得"""
        valid_mask = self.is_valid()
        if not valid_mask.any():
            return None
        return int(np.argmax(valid_mask))

    @property
    def first_invalid_index(self) -> Optional[int]:
        """最初の無効な値（None/NaN/Error str）のインデックスを取得"""
        # is_valid の逆
        valid_mask = self.is_valid()
        if valid_mask.all():
            return None
        return int(np.argmin(valid_mask))

    def to_numeric(self, errors: str = "raise") -> "NumberColumn":
        """数値を格納するColumnに変換する
        
        Args:
            errors: エラー処理の方法 ('raise', 'coerce', 'ignore')
                'raise': 変換できない値があるとエラー
                'coerce': 変換できない値はNaNにする
                'ignore': (未実装) 元の値を維持（NumberColumnにはならない可能性があるため非推奨）
                
        Returns:
            NumberColumn: 変換後の新しいカラム
        """
        values = self.values
        new_values = []
        
        # 既に数値配列の場合
        if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
             return NumberColumn(self.ch, self.name, self.unit, values.copy(), deepcopy(self.metadata))

        # 変換処理
        try:
            # 汎用的な変換 (pd.to_numeric のような挙動を目指す)
            # 文字列配列の場合
            for v in values:
                if v is None:
                    new_values.append(np.nan)
                    continue
                    
                try:
                    # まずfloat変換を試みる
                    if isinstance(v, str):
                        # "nan", "null" 等の処理
                        if v.lower() in ("nan", "null", "none", ""):
                            new_values.append(np.nan)
                        else:
                            new_values.append(float(v))
                    else:
                        new_values.append(float(v))
                except (ValueError, TypeError):
                    if errors == "coerce":
                        new_values.append(np.nan)
                    else:
                         raise ValueError(f"Unable to parse string '{v}' at position {len(new_values)}")
                         
            return NumberColumn(self.ch, self.name, self.unit, new_values, deepcopy(self.metadata))
            
        except Exception as e:
            if errors == "raise":
                raise e
            # ignoreの場合は自分自身を返す（型は変わらない）
            return self

    def clip(self, lower: Optional[float] = None, upper: Optional[float] = None) -> "Column":
        """値を範囲内に制限する
        
        Args:
             lower: 下限値
             upper: 上限値
             
        Returns:
             Column: 制約適用後の新しいColumn
        """
        # 数値カラムでない場合はエラーにするか、ベストエフォートでやるか
        # ここでは to_numeric せずに試みる
        
        try:
            values = np.array(self.values)
            
            # 数値型であれば np.clip が使える
            # None/NaN があると warning が出るかも知れないが機能はするはず
            
            # object型の場合は一旦float変換を試みるか、個別に比較する
            if values.dtype == object or not np.issubdtype(values.dtype, np.number):
                 # リスト内包表記で処理
                 new_values = []
                 for v in self.values:
                     if v is None:
                         new_values.append(None)
                         continue
                     try:
                         val = v
                         if lower is not None and val < lower:
                             val = lower
                         if upper is not None and val > upper:
                             val = upper
                         new_values.append(val)
                     except TypeError:
                         # 比較できない場合はそのまま
                         new_values.append(v)
                 return Column(self.ch, self.name, self.unit, new_values, deepcopy(self.metadata))
            
            # NumPyの数値配列の場合
            clipped_values = np.clip(values, lower, upper)
            # 元のクラスと同じクラスで返す
            return self.__class__(self.ch, self.name, self.unit, clipped_values, deepcopy(self.metadata))
            
        except Exception:
            return self.clone()

    def find_nearest_index(self, value: Any) -> int:
        """指定した値に最も近い要素のインデックスを返す"""
        # Stepの実装と同様に
        if len(self.values) == 0:
            return -1
            
        values = self.values
        
        # NumPy数値配列
        if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number):
             # NaNがある場合、それらは無視できないとargminがおかしくなる可能性がある
             # ここではNaNを除外するか、あるいはNaNとの比較結果（常にFalse?）に依存するか
             # np.abs(NaN - val) -> NaN
             # argmin(NaN含む) -> 最初のNaNのインデックスになることがある or 予期せぬ挙動
             
             # 安全にやるなら nanargmin を使うべきだが、絶対差分にNaNが含まれることになる
             diff = np.abs(values - value)
             if np.isnan(diff).all():
                 return -1
             return int(np.nanargmin(diff))
             
        # リストなどの場合
        try:
             # 数値変換して計算
             # 計算不能な要素（文字列など）やNoneは無視する
             min_diff = float('inf')
             min_idx = -1
             
             for i, v in enumerate(values):
                 if v is None:
                     continue
                 try:
                     diff = abs(v - value)
                     if diff < min_diff:
                         min_diff = diff
                         min_idx = i
                 except (TypeError, ValueError):
                     continue
            
             return min_idx
        except Exception:
             return -1

    def find_nearest(self, value: Any) -> Any:
        """指定した値に最も近い要素の値を返す"""
        idx = self.find_nearest_index(value)
        if idx == -1:
            return None
        return self.values[idx]


class NumberColumn(Column):
    """数値型データのみを格納するカラムクラス"""

    def __init__(self, ch, name, unit, values=None, metadata=None):
        # 値が数値型かどうか検証
        if values is not None:
            # Noneは許容するが、それ以外は数値型であることを確認
            # NumPy配列化の前にリストとして検証するか、変換後に検証するか
            # ここでは変換前（または既存の配列）をチェック
            pass 
            
        # DataHolderの初期化でNumPy配列化される
        # NumberColumnの場合はfloat型に変換し、NoneをNaNにする
        
        converted_values = None
        if values is not None:
            if isinstance(values, np.ndarray):
                if np.issubdtype(values.dtype, np.number):
                    converted_values = values.astype(float)
                else:
                    # オブジェクト配列などをfloatに変換（エラーチェック付き）
                     converted_values = np.array(values, dtype=float)
            else:
                # リストから変換。Noneはnp.nanになる(floatの場合)
                # ただし、文字列などが混じっているとエラーになるので検証が必要
                try:
                    # Noneが含まれているとfloat変換でNaNになる
                    converted_values = np.array(values, dtype=float)
                except (ValueError, TypeError):
                     # 詳細なエラーメッセージのために元のバリデーションを呼ぶ
                     self._validate_numeric_values(values)
                     raise

        super().__init__(ch, name, unit, converted_values, metadata)

    def _validate_numeric_values(self, values: Any) -> None:
        """値が数値型かNoneであることを検証"""
        # NumPy配列の場合はdtypeチェック
        if isinstance(values, np.ndarray):
             if not np.issubdtype(values.dtype, np.number):
                  raise TypeError("NumPy配列は数値型である必要があります")
             return

        for i, value in enumerate(values):
            if value is not None and not isinstance(value, (int, float, np.number)):
                raise TypeError(
                    f"値はnumeric型またはNoneである必要があります。インデックス {i} の値: {value}"
                )

    def clone(self):
        """NumberColumnのクローンを作成"""
        return NumberColumn(
            self.ch,
            self.name,
            self.unit,
        self.values.copy(), # deepcopyではなくcopy()で十分（数値配列なので）
            deepcopy(self.metadata),
        )

    def mean(self) -> Optional[float]:
        """平均値を取得"""
        if len(self.values) == 0:
            return None
        # nanmeanを使うとNaNを無視して計算できる
        # 全てNaNの場合は警告が出るので抑制するか、事前にチェック
        if np.isnan(self.values).all():
             return None
        return float(np.nanmean(self.values))

    def median(self) -> Optional[float]:
        """中央値を取得"""
        if len(self.values) == 0:
            return None
        if np.isnan(self.values).all():
             return None
        return float(np.nanmedian(self.values))

    def std(self) -> Optional[float]:
        """標準偏差を取得"""
        if len(self.values) <= 1:
            return None
        # 自由度1 (ddof=1) で計算
        # 有効な値が1つ以下の場合はNaNが返るはず
        if np.isnan(self.values).sum() >= len(self.values) - 1:
             return None
        return float(np.nanstd(self.values, ddof=1))

    def sum(self) -> float:
        """合計値を取得"""
        if len(self.values) == 0:
            return 0.0
        return float(np.nansum(self.values))

    def variance(self) -> Optional[float]:
        """分散を取得"""
        if len(self.values) <= 1:
            return None
        if np.isnan(self.values).sum() >= len(self.values) - 1:
             return None
        return float(np.nanvar(self.values, ddof=1))

    def quantile(self, q: float) -> Optional[float]:
        """指定したパーセンタイルの値を取得"""
        if not 0 <= q <= 1:
            raise ValueError("qは0から1の間の値である必要があります")

        if len(self.values) == 0:
            return None
        if np.isnan(self.values).all():
             return None

        return float(np.nanquantile(self.values, q))


class StringColumn(Column):
    """文字列型データのみを格納するカラムクラス"""

    def __init__(self, ch, name, unit, values=None, metadata=None):
        # 値が文字列型かどうか検証
        if values is not None:
            # Noneは許容するが、それ以外は文字列型であることを確認
            self._validate_string_values(values)

        super().__init__(ch, name, unit, values, metadata)

    def _validate_string_values(self, values: List[Any]) -> None:
        """値が文字列型かNoneであることを検証"""
        for i, value in enumerate(values):
            if value is not None and not isinstance(value, str):
                raise TypeError(
                    f"値はstring型またはNoneである必要があります。インデックス {i} の値: {value}"
                )

    def clone(self):
        """StringColumnのクローンを作成"""
        return StringColumn(
            self.ch,
            self.name,
            self.unit,
            deepcopy(self.values),
            deepcopy(self.metadata),
        )


class InvalidColumn(Column):
    """全ての値がNoneである無効な列を表すクラス"""

    def __init__(self, ch, name, unit, values=None, metadata=None):
        # 値がすべてNoneであることを確認
        if values is not None and any(value is not None for value in values):
            raise ValueError("InvalidColumnの全ての値はNoneである必要があります")

        super().__init__(ch, name, unit, values, metadata)

    def clone(self):
        """InvalidColumnのクローンを作成"""
        return InvalidColumn(
            self.ch,
            self.name,
            self.unit,
            deepcopy(self.values),
            deepcopy(self.metadata),
        )

    def sum(self) -> float:
        """合計値を取得（常に0を返す）"""
        return 0.0


# 補助関数
def detect_column_type(ch, name, unit, values=None, metadata=None) -> Column:
    """
    データ内容に基づいて適切なColumnクラスのインスタンスを生成する

    Args:
        ch: チャンネル
        name: カラム名
        unit: 単位
        values: 値のリスト
        metadata: メタデータ

    Returns:
        Column: 適切なColumnサブクラスのインスタンス
    """
    # 値がNoneまたは空の場合は標準のColumnを返す
    if values is None or len(values) == 0:
        return Column(ch, name, unit, values, metadata)

    # 全ての値がNoneの場合はInvalidColumnを返す
    if all(v is None for v in values):
        return InvalidColumn(ch, name, unit, values, metadata)

    # None以外の値を収集
    non_none_values = [v for v in values if v is not None]

    # 型を判定
    try:
        # 全ての値が数値型かどうか確認
        if all(isinstance(v, (int, float, np.number)) for v in non_none_values):
            return NumberColumn(ch, name, unit, values, metadata)

        # 全ての値が文字列型かどうか確認
        if all(isinstance(v, str) for v in non_none_values):
            return StringColumn(ch, name, unit, values, metadata)

        # それ以外の場合は標準のColumnを返す
        return Column(ch, name, unit, values, metadata)
    except Exception as e:
        # エラーが発生した場合は安全のため標準のColumnを返す
        return Column(ch, name, unit, values, metadata)


def create_column_from_values(
    ch, name, unit, values=None, metadata=None, column_type=None
) -> Column:
    """
    指定した値と型からカラムを生成する

    Args:
        ch: チャンネル
        name: カラム名
        unit: 単位
        values: 値のリスト
        metadata: メタデータ
        column_type: カラム型（指定なしの場合は自動判定）

    Returns:
        Column: 生成されたColumnインスタンス
    """
    # 型が指定されている場合はその型でカラムを生成
    if column_type is not None:
        column_classes = {
            "number": NumberColumn,
            "string": StringColumn,
            "invalid": InvalidColumn,
            "default": Column,
        }

        column_class = column_classes.get(column_type.lower(), Column)
        return column_class(ch, name, unit, values, metadata)

    # 型が指定されていない場合はデータ内容から自動判定
    return detect_column_type(ch, name, unit, values, metadata)
