"""汎用操作 (`collection.ops`) の実装"""

from __future__ import annotations

import inspect
import math
import warnings
from typing import (
    TYPE_CHECKING, Any, Callable, Concatenate, Dict, Generic, List, Optional, ParamSpec, Self, Sequence,
    TypeVar, Union,
)

import numpy as np
import polars as pl

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import KEEP, Column
from tascpy.core.result import PointResult
from tascpy.core.row import Row
from tascpy.numeric import combine as f_combine
from tascpy.numeric import math as f_math
from tascpy.numeric import stats as f_stats

if TYPE_CHECKING:
    from .ops_list import OpsList

C_co = TypeVar("C_co", bound=ColumnCollection, covariant=True)
D = TypeVar("D", bound=ColumnCollection)
P = ParamSpec("P")
# OpsList[Self] は jedi（marimo の補完）が要素の型を解決できないため、分割系は self を TypeVar で受ける
S = TypeVar("S", bound="CoreOps[Any]")

Operand = Union[str, float, int, np.ndarray, Sequence[float]]

_MISSING_TOKENS = {"none", "null", "", "nan", "na"}


def _to_float(v: Any) -> float:
    if v is None:
        return np.nan
    if isinstance(v, str):
        s = v.strip().lower()
        if s in _MISSING_TOKENS or s.startswith("*"):
            return np.nan
    try:
        return float(v)
    except (TypeError, ValueError):
        return np.nan


def to_float_array(values: Any) -> np.ndarray:
    """値の並びを float 配列に変換する（None や "*****" などの欠損表記は NaN）"""
    arr = np.asarray(values)
    if np.issubdtype(arr.dtype, np.number):
        return arr.astype(float)
    return np.array([_to_float(v) for v in arr.ravel()], dtype=float).reshape(arr.shape)


class CoreOps(Generic[C_co]):
    """ColumnCollection に対するメソッドチェーン用の操作クラス

    各操作は新しいコレクションを生成し、同じ型の操作オブジェクトを返します。
    `end()` でチェーンを終了し、コレクションを取り出します。

    結果列の単位は `unit=` で明示できます。省略時は演算の種類に応じて決まり、
    自明でない場合は None（不明）になります（docs/developer_guide_design.md 参照）。

    Examples:
        >>> result = col.ops.add("CH1", "CH2", result_column="合計").filter_by_value("状態", "正常").end()
        >>> result.columns
        ['荷重', '変位', 'CH1', 'CH2', 'CH3', '状態', '合計']
        >>> len(col), len(result)
        (6, 5)
    """

    def __init__(self, collection: C_co) -> None:
        self._collection = collection

    @property
    def _c(self) -> C_co:
        return self._collection

    def _next(self, collection: ColumnCollection) -> Self:
        return type(self)(collection)  # type: ignore[arg-type]

    def end(self) -> C_co:
        """操作チェーンを終了し、コレクションを返します"""
        return self._collection

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self._collection!r}>"

    # ── 内部ヘルパー ───────────────────────────────

    def _is_column(self, operand: Any) -> bool:
        return isinstance(operand, str) and operand in self._c

    def _column_values(self, name: str) -> np.ndarray:
        return self._c[name].values

    def _raw(self, operand: Any) -> Any:
        """列名なら列の値配列、配列風なら ndarray、それ以外はそのまま返す"""
        if isinstance(operand, str):
            return self._column_values(operand)
        if isinstance(operand, (list, tuple)):
            return np.asarray(operand)
        return operand

    def _numeric(self, operand: Any) -> Any:
        """列名・配列を欠損 NaN の float 配列に変換する（スカラーはそのまま）

        Raises:
            TypeError: 数値列でない列を指定した場合
        """
        if isinstance(operand, str):
            column = self._c[operand]
            if not column.is_numeric:
                raise TypeError(f"列 '{operand}' は数値列ではありません (dtype={column.dtype})")
            return column.values
        if isinstance(operand, (list, tuple, np.ndarray)):
            return to_float_array(operand)
        return operand

    def _unit_of(self, operand: Any) -> Optional[str]:
        return self._c.meta[operand].unit if self._is_column(operand) else None

    def _first_unit(self, *operands: Any) -> Optional[str]:
        """列名である最初の引数の単位"""
        for operand in operands:
            if self._is_column(operand):
                return self._unit_of(operand)
        return None

    def _scaled_unit(self, value1: Any, value2: Any) -> Optional[str]:
        """列とスカラーの積・商ならその列の単位、それ以外は None"""
        if self._is_column(value1) and np.ndim(value2) == 0 and not isinstance(value2, str):
            return self._unit_of(value1)
        if self._is_column(value2) and np.ndim(value1) == 0 and not isinstance(value1, str):
            return self._unit_of(value2)
        return None

    def _numeric_columns(self, columns: Optional[List[str]]) -> List[str]:
        """指定した列（省略時は全数値列）。数値でない列を指定すると TypeError"""
        if columns is None:
            return [name for name in self._c.columns if self._c[name].is_numeric]
        names = self._check_columns(columns)
        for name in names:
            self._numeric(name)
        return names

    def _stack_numeric(self, names: List[str], label: str) -> np.ndarray:
        """数値列を (列数, 行数) の float 配列に積む（欠損は NaN）"""
        if not names:
            raise ValueError(f"{label}対象の列が指定されていません")
        return np.vstack([np.asarray(self._numeric(n), dtype=float) for n in names])

    def _check_columns(self, columns: Optional[List[str]]) -> List[str]:
        names = self._c.columns if columns is None else list(columns)
        for name in names:
            if name not in self._c:
                raise KeyError(f"列 '{name}' が存在しません")
        return names

    def _with_column(self, name: str, values: Any, unit: Optional[str], ch: Optional[str],
                     default_unit: Optional[str] = None) -> Self:
        """結果列を追加・上書きした新しいコレクション（単位は unit、なければ default_unit）"""
        return self._next(self._c.with_column(
            name, values, unit=unit if unit is not None else default_unit, ch=KEEP if ch is None else ch,
        ))

    @staticmethod
    def _point(name: str, outcome: tuple, x_unit: Optional[str] = None,
               y_unit: Optional[str] = None) -> PointResult:
        """(is_valid, x, y, info) 形式の計算結果を PointResult にする（is_valid は metadata に入れる）"""
        is_valid, x, y = outcome[0], outcome[1], outcome[2]
        info = dict(outcome[3]) if len(outcome) > 3 else {}
        info["is_valid"] = is_valid
        return PointResult(name=name, x=x, y=y, x_unit=x_unit, y_unit=y_unit, metadata=info)

    def _with_rows(self, rows: Any, **metadata: Any) -> Self:
        result = self._c.take(rows)
        return self._next(result.with_metadata(**metadata) if metadata else result)

    def _mask(self, expr: pl.Expr) -> np.ndarray:
        return self._c.df.select(expr.fill_null(False)).to_series().to_numpy()

    def _split(self: S, row_groups: List[Any], keys: Optional[List[Any]] = None) -> "OpsList[S]":
        from .ops_list import OpsList

        return OpsList([self._next(self._c.take(rows)) for rows in row_groups], keys)

    def _binary(self, func: Callable, value1: Operand, value2: Operand, result_column: str,
                unit: Optional[str], ch: Optional[str], default_unit: Optional[str]) -> Self:
        values = func(self._numeric(value1), self._numeric(value2))
        return self._with_column(result_column, values, unit, ch, default_unit)

    # ── チェーン制御・ドメイン変換 ───────────────────

    def pipe(self, func: Callable[[ColumnCollection], ColumnCollection]) -> Self:
        """コレクションを受け取りコレクションを返す任意の関数を適用します

        Examples:
            >>> len(col.ops.pipe(lambda c: c.head(3)).end())
            3
        """
        return self._next(func(self._c))

    def debug(self, message: Optional[str] = None) -> Self:
        """コレクションの状態を表示し、自身を返します"""
        if message:
            print(f"DEBUG: {message}")
        print(f"Collection: {self._c}")
        print(f"Domain: {self._c.domain}")
        print(f"Units: {self._c.units}")
        print(f"metadata: {dict(self._c.metadata)}")
        return self

    def as_core(self) -> "CoreOps[ColumnCollection]":
        """ドメイン固有の設定を外し、汎用コレクションに変換します"""
        return CoreOps(self._c._as_class(ColumnCollection))

    def end_as(self, factory: Callable[Concatenate[ColumnCollection, P], D],
               /, *args: P.args, **kwargs: P.kwargs) -> D:
        """操作チェーンを終了し、ドメインのコレクションに変換して返します

        factory には各ドメインの変換関数（`tascpy.as_load_displacement` など、`from_collection` の別名）を渡します。
        残りの引数は factory に渡され、型チェッカーと IDE の補完もそのシグネチャに従います。
        変換後のドメインの操作は `.ops` で続けます。

        Examples:
            >>> from tascpy.domains import as_load_displacement
            >>> ld = col.ops.end_as(as_load_displacement, load_column="荷重", displacement_column="変位")
            >>> type(ld).__name__, ld.load_column
            ('LoadDisplacementCollection', '荷重')
            >>> type(ld.ops).__name__
            'LoadDisplacementOps'
        """
        return factory(self._c, *args, **kwargs)

    # ── 四則演算 ─────────────────────────────────

    def add(self, value1: Operand, value2: Operand, *, result_column: str,
            unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """要素ごとの和を新しい列として追加します

        Args:
            value1: 第1引数（列名または数値・配列）
            value2: 第2引数（列名または数値・配列）
            result_column: 結果列名（既存列を指定すると上書き）
            unit: 結果の単位（省略時は最初の列の単位）
            ch: 結果のチャンネル名

        Examples:
            >>> col.ops.add("CH1", "CH2", result_column="合計").end()["合計"].values
            array([  0., 150., 300., 450., 600., 750.])
            >>> col.ops.add("CH1", 10.5, result_column="補正後").end()["補正後"].unit
            'ue'
        """
        return self._binary(np.add, value1, value2, result_column, unit, ch,
                            self._first_unit(value1, value2))

    def subtract(self, value1: Operand, value2: Operand, *, result_column: str,
                 unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """要素ごとの差 (value1 - value2) を新しい列として追加します（単位は最初の列の単位）"""
        return self._binary(np.subtract, value1, value2, result_column, unit, ch,
                            self._first_unit(value1, value2))

    def multiply(self, value1: Operand, value2: Operand, *, result_column: str,
                 unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """要素ごとの積を新しい列として追加します（単位は列×スカラーならその列の単位、それ以外は None）"""
        return self._binary(np.multiply, value1, value2, result_column, unit, ch,
                            self._scaled_unit(value1, value2))

    def divide(self, value1: Operand, value2: Operand, *, result_column: str,
               unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """要素ごとの商 (value1 / value2) を新しい列として追加します（単位の規則は multiply と同じ）

        Raises:
            ValueError: 有効な分子に対して分母が 0 の場合
        """
        numerator, denominator = self._numeric(value1), self._numeric(value2)
        if np.ndim(denominator) == 0:
            if denominator == 0:
                raise ValueError("ゼロによる除算が発生しました")
        else:
            zero = denominator == 0
            if np.any(~np.isnan(np.broadcast_to(numerator, zero.shape)[zero])):
                raise ValueError("ゼロによる除算が発生しました")
        with np.errstate(divide="ignore", invalid="ignore"):
            values = np.divide(numerator, denominator)
        return self._with_column(result_column, values, unit, ch, self._scaled_unit(value1, value2))

    # ── 微分・積分 ───────────────────────────────

    def _strict_pair(self, y_column: Operand, x_column: Operand):
        y, x = self._numeric(y_column), self._numeric(x_column)
        has_missing = np.isnan(y).any() or np.isnan(x).any()
        return y, x, has_missing

    def _compound_unit(self, y_column: Operand, x_column: Operand, sep: str) -> Optional[str]:
        y_unit, x_unit = self._unit_of(y_column), self._unit_of(x_column)
        return f"{y_unit}{sep}{x_unit}" if y_unit and x_unit else None

    def diff(self, y_column: Operand, x_column: Operand, method: str = "central",
             *, result_column: str, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """離散微分 dy/dx を新しい列として追加します（単位は "y/x"）

        計算できない点は欠損です（欠損の前後、x が変化しない区間、forward の最後の点、backward の最初の点）。
        backward は隣り合う点の傾き（荷重-変位なら接線剛性）です。

        Args:
            y_column: Y データの列名
            x_column: X データの列名
            method: 微分手法 ("central", "forward", "backward")

        Examples:
            >>> col.ops.diff("荷重", "変位", method="backward", result_column="接線剛性").end()["接線剛性"].values.round(1)
            array([ nan, 40. , 40. , 20. ,  5. ,  1.7])
        """
        values = f_math.diff(self._numeric(x_column), self._numeric(y_column), method=method)
        return self._with_column(result_column, values, unit, ch,
                                 self._compound_unit(y_column, x_column, "/"))

    def integrate(self, y_column: Operand, x_column: Operand, method: str = "trapezoid", initial_value: float = 0.0,
                  *, result_column: str, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """離散積分 ∫y dx を新しい列として追加します（欠損を含む場合は全て欠損、単位は "y*x"）

        Args:
            method: 積分手法 ("trapezoid" のみ。データの並び順に沿って積分)
            initial_value: 積分定数
        """
        y, x, has_missing = self._strict_pair(y_column, x_column)
        values = (np.full(len(y), np.nan) if has_missing
                  else f_math.integrate(x, y, method=method, initial_value=initial_value))
        return self._with_column(result_column, values, unit, ch,
                                 self._compound_unit(y_column, x_column, "*"))

    def calculate(self, func: Callable[..., Any], *, result_column: str,
                  columns: Optional[Dict[str, str]] = None, unit: Optional[str] = None,
                  ch: Optional[str] = None) -> Self:
        """関数の引数名を列名として各列の値（float の numpy 配列、欠損は NaN）を渡し、戻り値を新しい列として追加します

        Args:
            func: 列の値を受け取って配列（またはスカラー）を返す関数
            result_column: 結果列名（既存列を指定すると上書き）
            columns: 引数名と列名が異なる場合の対応 {引数名: 列名}（列名が識別子として使えない場合など）
            unit: 結果の単位（省略時は None）
            ch: 結果のチャンネル名

        Raises:
            ValueError: func が可変長引数を持つ場合、または戻り値の長さが行数と一致しない場合
            KeyError: 引数に対応する列がない場合
            TypeError: 数値列でない列を使った場合

        Examples:
            >>> secant = col.tail(5).ops.calculate(lambda 荷重, 変位: 荷重 / 変位, result_column="割線剛性", unit="kN/mm").end()
            >>> secant["割線剛性"].values.round(1), secant["割線剛性"].unit
            (array([40. , 40. , 33.3, 22. , 14.4]), 'kN/mm')
            >>> col.ops.calculate(lambda p: p * 2, columns={"p": "荷重"}, result_column="P2").end()["P2"].values
            array([  0.,  80., 160., 200., 220., 230.])
            >>> col.ops.calculate(lambda CH1: np.where(CH1 > 250, CH1, 0), result_column="clipped").end()["clipped"].values
            array([  0.,   0.,   0., 300., 400., 500.])
        """
        mapping = dict(columns or {})
        positional: List[np.ndarray] = []
        keywords: Dict[str, np.ndarray] = {}
        for param in inspect.signature(func).parameters.values():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                raise ValueError("calculate の関数には可変長引数 (*args / **kwargs) を使えません")
            name = mapping.get(param.name, param.name)
            if name not in self._c:
                raise KeyError(f"引数 '{param.name}' に対応する列 '{name}' が存在しません")
            value = np.array(self._numeric(name))
            if param.kind == param.POSITIONAL_ONLY:
                positional.append(value)
            else:
                keywords[param.name] = value

        values = np.asarray(func(*positional, **keywords), dtype=float)
        if values.ndim == 0:
            values = np.full(len(self._c), float(values))
        if values.shape != (len(self._c),):
            raise ValueError(f"関数の戻り値の形 {values.shape} が行数 ({len(self._c)}) と一致しません")
        return self._with_column(result_column, values, unit, ch)

    # ── 単項変換 ─────────────────────────────────

    def log(self, values: Operand, base: float = math.e, *, result_column: str,
            unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """対数を新しい列として追加します（単位は None）"""
        return self._with_column(result_column, f_math.log(self._numeric(values), base=base), unit, ch)

    def sqrt(self, values: Operand, *, result_column: str,
             unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """平方根を新しい列として追加します（単位は None）"""
        with np.errstate(invalid="ignore"):
            result = np.sqrt(self._numeric(values))
        return self._with_column(result_column, result, unit, ch)

    def pow(self, values: Operand, exponent: float = 1.0, *, result_column: str,
            unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """べき乗を新しい列として追加します（単位は None）"""
        with np.errstate(invalid="ignore"):
            result = np.power(self._numeric(values), exponent)
        return self._with_column(result_column, result, unit, ch)

    def abs(self, values: Operand, *, result_column: str,
                   unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """絶対値を新しい列として追加します"""
        return self._with_column(result_column, np.abs(self._numeric(values)), unit, ch, self._unit_of(values))


    def round(self, values: Operand, decimals: int = 0, *, result_column: str,
                     unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """四捨五入した値を新しい列として追加します"""
        return self._with_column(result_column, np.round(self._numeric(values), decimals), unit, ch, self._unit_of(values))

    def normalize(self, values: Operand, method: str = "minmax", *, result_column: str,
                  unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """正規化した値を新しい列として追加します（単位は ""）

        Args:
            method: 正規化手法 ("minmax", "zscore")
        """
        return self._with_column(result_column, f_math.normalize(self._numeric(values), method=method), unit, ch, "")

    # ── 統計 ──────────────────────────────────

    def moving_average(self, column: Operand, window_size: int = 3,
                       *, result_column: str, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """移動平均を新しい列として追加します

        Args:
            window_size: ウィンドウサイズ
        """
        values = f_stats.moving_average(self._numeric(column), window_size=window_size)
        return self._with_column(result_column, values, unit, ch, self._unit_of(column))

    def detect_outliers(self, column: Operand, window_size: int = 3, threshold: float = 0.5,
                        min_abs_value: float = 1e-10, scale_factor: float = 1.0,
                        *, result_column: str, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """外れ値フラグ（0: 正常, 1: 外れ値）を新しい列として追加します"""
        flags = f_stats.detect_outliers(
            self._numeric(column), window_size=window_size, threshold=threshold,
            min_abs_value=min_abs_value, scale_factor=scale_factor,
        )
        return self._with_column(result_column, flags, unit, ch, "")

    def gaussian_filter(self, column: Operand, sigma: float = 1.0, window_size: Optional[int] = None,
                        *, result_column: str, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """ガウシアンフィルタで平滑化した値を新しい列として追加します"""
        values = f_stats.gaussian_filter(self._numeric(column), sigma=sigma, window_size=window_size)
        return self._with_column(result_column, values, unit, ch, self._unit_of(column))

    # ── 列の合成 ───────────────────────────────

    def switch_by_step(self, v1: Operand, v2: Operand, threshold: Union[int, float] = 0, compare_mode: str = "value",
                       by_step_value: bool = True, tolerance: Optional[float] = None,
                       *, result_column: str, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """ステップ値（またはインデックス）の閾値を境に v1 から v2 へ切り替えた列を追加します"""
        values = f_combine.switch_by_step(
            steps=self._c.step, v1=self._raw(v1), v2=self._raw(v2), threshold=threshold,
            compare_mode=compare_mode, by_step_value=by_step_value, tolerance=tolerance,
        )
        return self._with_column(result_column, values, unit, ch, self._unit_of(v1))

    def blend_by_step(self, v1: Operand, v2: Operand, start: Union[int, float] = 0, end: Union[int, float] = 1,
                      compare_mode: str = "value", by_step_value: bool = True, blend_method: str = "linear",
                      tolerance: Optional[float] = None,
                      *, result_column: str, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """ステップ区間 [start, end] で v1 から v2 へ滑らかにブレンドした列を追加します

        Args:
            blend_method: ブレンド手法 ("linear", "smooth", "log", "exp")
        """
        values = f_combine.blend_by_step(
            steps=self._c.step, v1=self._raw(v1), v2=self._raw(v2), start=start, end=end,
            compare_mode=compare_mode, by_step_value=by_step_value, blend_method=blend_method, tolerance=tolerance,
        )
        return self._with_column(result_column, values, unit, ch, self._unit_of(v1))

    def sum_columns(self, columns: Optional[List[str]] = None, *, result_column: str,
                    unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """複数列を行ごとに合計した列を追加します（省略時は全数値列、欠損を含む行は欠損）"""
        names = self._numeric_columns(columns)
        values = np.sum(self._stack_numeric(names, "合計"), axis=0)
        return self._with_column(result_column, values, unit, ch, self._first_unit(*names))

    def average_columns(self, columns: Optional[List[str]] = None, ignore_nan: bool = True,
                        *, result_column: str, unit: Optional[str] = None,
                        ch: Optional[str] = None) -> Self:
        """複数列を行ごとに平均した列を追加します（省略時は全数値列）

        Args:
            columns: 平均する列
            ignore_nan: True なら欠損を除いて平均（全て欠損の行は欠損）、False なら欠損を含む行は欠損

        Examples:
            >>> col.ops.average_columns(["CH1", "CH2", "CH3"], result_column="平均").end()["平均"].values
            array([  0.,  40.,  80., 120., 160., 200.])
        """
        names = self._numeric_columns(columns)
        stacked = self._stack_numeric(names, "平均")
        with np.errstate(invalid="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)  # 全て欠損の行の nanmean
            values = np.nanmean(stacked, axis=0) if ignore_nan else np.mean(stacked, axis=0)
        return self._with_column(result_column, values, unit, ch, self._first_unit(*names))

    def conditional_select(self, v1: Operand, v2: Operand, cond_values: Operand, threshold: Union[int, float] = 0,
                           compare: str = ">", *, result_column: str,
                           unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """条件列と閾値の比較結果が真なら v1、偽なら v2 を選んだ列を追加します

        Args:
            compare: 比較演算子 (">", "<", ">=", "<=", "==", "!=")
        """
        values = f_combine.conditional_select(
            v1=self._raw(v1), v2=self._raw(v2), cond_values=self._raw(cond_values),
            threshold=threshold, compare=compare,
        )
        return self._with_column(result_column, values, unit, ch, self._unit_of(v1))

    def custom_combine(self, v1: Operand, v2: Operand, combine_func: Callable[[Any, Any], Any],
                       *, result_column: str,
                       unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """任意の関数で 2 列を合成した列を追加します（単位は unit で指定、省略時は None）

        Examples:
            >>> col.ops.custom_combine("CH1", "CH2", lambda x, y: x - y, result_column="diff").end().columns[-1]
            'diff'
        """
        values = f_combine.custom_combine(v1=self._raw(v1), v2=self._raw(v2), combine_func=combine_func)
        return self._with_column(result_column, values, unit, ch)

    # ── 行の抽出・除外 ─────────────────────────────

    def join(self, other: Union["CoreOps[Any]", ColumnCollection]) -> Self:
        """ステップが同じ別の表の列を横に足します（集約した表を並べるときなど。列のメタは引き継ぐ）

        Raises:
            ValueError: ステップが一致しない場合、列名が重なる場合

        Examples:
            >>> parts = col.ops.split_by_integers([1, 1, 1, 2, 2, 2])
            >>> peak = parts.collect(lambda o: o.end()["荷重"].max()).to_table(name="peak")
            >>> rows = parts.collect(lambda o: len(o.end())).to_table(name="rows")
            >>> peak.join(rows).end().columns
            ['peak', 'rows']
        """
        right = other.end() if isinstance(other, CoreOps) else other
        if len(right) != len(self._c) or not np.array_equal(right.step, self._c.step):
            raise ValueError("ステップが一致しない表は結合できません")
        overlap = [name for name in right.columns if name in self._c]
        if overlap:
            raise ValueError(f"列名が重なっています: {overlap}")
        collection = self._c
        for name in right.columns:
            collection = collection.with_column(name, right[name])
        return self._next(collection)

    def select(self, columns: Optional[List[str]] = None, indices: Optional[List[int]] = None,
               steps: Optional[List[Union[int, float]]] = None, by_step_value: bool = True,
               tolerance: Optional[float] = None) -> Self:
        """列・行インデックス・ステップ値を指定してデータを抽出します

        ステップ指定時は、見つかったステップと見つからなかったステップを
        メタデータ "selected_steps" / "missing_steps" に記録します。

        Args:
            columns: 抽出する列名（省略時は全列）
            indices: 抽出する行インデックス
            steps: 抽出するステップ値（by_step_value=False ならインデックス）
            tolerance: ステップ値一致判定の許容誤差

        Raises:
            KeyError: 存在しない列を指定した場合
            ValueError: indices と steps を同時に指定した場合
        """
        if indices is not None and steps is not None:
            raise ValueError("indices と steps は同時に指定できません")
        collection = self._c if columns is None else self._c.select(self._check_columns(columns))
        if indices is not None:
            return self._next(collection.take(indices))
        if steps is None:
            return self._next(collection)

        rows, missing = [], []
        for target in steps:
            if by_step_value:
                idx = collection.step_index(target, tolerance=tolerance)
            else:
                idx = target if 0 <= target < len(collection) else None
            if idx is None:
                missing.append(target)
            else:
                rows.append(idx)
        selected = collection.take(rows)
        return self._next(selected.with_metadata(
            selected_steps=selected.step.tolist(), missing_steps=missing, by_step_value=by_step_value,
        ))

    def nearest_row(self, column: str, value: float) -> Row:
        """指定列の値が value に最も近い 1 行を返します（データの行を選ぶ値への集約）

        Raises:
            ValueError: 列が数値でない、または有効な値がない場合

        Examples:
            >>> row = col.ops.nearest_row("荷重", 100.0)
            >>> row["荷重"], row.unit("荷重"), row.step
            (100.0, 'kN', 4)
        """
        idx = self._c[column].nearest_index(value)
        if idx is None:
            raise ValueError(f"列 '{column}' に比較できる数値がありません")
        return self._c[idx]

    def filter_by_value(self, column: str, value: Any, tolerance: Optional[float] = None) -> Self:
        """指定列の値が value と一致する（tolerance 指定時は ±tolerance 以内の）行を抽出します

        Examples:
            >>> col.ops.filter_by_value("状態", "正常").end().step.tolist()
            [1, 2, 4, 5, 6]
            >>> col.ops.filter_by_value("荷重", 100.0, tolerance=15.0).end()["荷重"].values
            array([100., 110., 115.])
        """
        self._check_columns([column])
        expr = (pl.col(column) == value if tolerance is None
                else pl.col(column).is_between(value - tolerance, value + tolerance))
        return self._with_rows(self._mask(expr))

    def filter_by_condition(self, column: str, condition: Callable[[Any], bool]) -> Self:
        """指定列の各値に condition を適用し、True の行を抽出します（欠損の行は除外）

        Examples:
            >>> col.ops.filter_by_condition("荷重", lambda x: x >= 50).end().step.tolist()
            [3, 4, 5, 6]
        """
        values = self._c[column].to_list()
        return self._with_rows([v is not None and bool(condition(v)) for v in values])

    def filter_out_none(self, columns: Optional[List[str]] = None, mode: str = "any") -> Self:
        """欠損値を含む行を除外します

        Args:
            columns: 判定対象の列（省略時は全列）
            mode: "any" はいずれかが欠損、"all" は全てが欠損の行を除外
        """
        if mode not in ("any", "all"):
            raise ValueError("mode は 'any' または 'all' で指定してください")
        valid = [pl.col(n).is_not_null() for n in self._check_columns(columns)]
        if not valid:
            return self._next(self._c)
        return self._with_rows(self._mask(pl.all_horizontal(valid) if mode == "any" else pl.any_horizontal(valid)))

    def remove_consecutive_duplicates_across(self, columns: Optional[List[str]] = None) -> Self:
        """指定列（省略時は全列）の値がすべて直前の行と同じ行を除外します"""
        changed = [pl.col(n).ne_missing(pl.col(n).shift(1)) for n in self._check_columns(columns)]
        if not changed or len(self._c) == 0:
            return self._next(self._c)
        first = pl.int_range(pl.len()) == 0
        return self._with_rows(self._mask(first | pl.any_horizontal(changed)))

    def remove_outliers(self, column: str, window_size: int = 3, threshold: float = 0.5,
                        min_abs_value: float = 1e-10, scale_factor: float = 1.0) -> Self:
        """外れ値と判定された行を除外します"""
        flags = f_stats.detect_outliers(
            self._numeric(column), window_size=window_size, threshold=threshold,
            min_abs_value=min_abs_value, scale_factor=scale_factor,
        )
        return self._with_rows(np.asarray(flags) == 0)

    def remove_steps(self, steps: List[Any], tolerance: Optional[float] = None) -> Self:
        """指定したステップ値の行を除外します"""
        current = self._c.step
        if tolerance is None:
            keep = ~np.isin(current, steps)
        else:
            diff = np.abs(current.astype(float)[:, None] - np.asarray(steps, dtype=float)[None, :])
            keep = ~np.any(diff <= tolerance, axis=1)
        return self._with_rows(keep)

    # ── 分割 ─────────────────────────────────

    def split_by_integers(self: S, markers: Union[str, List[int], np.ndarray]) -> "OpsList[S]":
        """行ごとの整数マーカー（列名または配列）の値ごとにコレクションを分割します（欠損の行は除外）

        各要素のキー（`OpsList.keys`）はマーカーの値です。

        Examples:
            >>> parts = col.ops.split_by_integers([1, 1, 1, 2, 2, 3])
            >>> [len(c) for c in parts.end()], parts.keys
            ([3, 2, 1], [1, 2, 3])
        """
        values = to_float_array(self._raw(markers))
        if len(values) != len(self._c):
            raise ValueError(f"マーカーの長さ ({len(values)}) が行数 ({len(self._c)}) と一致しません")
        keys = np.unique(values[~np.isnan(values)])
        return self._split([np.flatnonzero(values == k) for k in keys], keys.tolist())

    def split_at_indices(self: S, indices: Union[int, List[int]]) -> "OpsList[S]":
        """指定したインデックスでコレクションを分割します（各要素のキーは区間の番号 0, 1, ...）

        Raises:
            IndexError: インデックスが 0〜行数 の範囲外の場合
        """
        length = len(self._c)
        points = sorted({indices} if isinstance(indices, int) else set(indices))
        for idx in points:
            if not 0 <= idx <= length:
                raise IndexError(f"インデックス {idx} は範囲外です (0-{length})")
        bounds = sorted({0, *points, length})
        return self._split([np.arange(a, b) for a, b in zip(bounds[:-1], bounds[1:])])
