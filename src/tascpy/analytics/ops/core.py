"""汎用操作 (`collection.ops`) の実装"""

from __future__ import annotations

import ast
import math
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, List, Optional, Self, Sequence, TypeVar, Union

import numpy as np

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column, NumberColumn, detect_column_type
from tascpy.core.result import AnalysisResult, PointResult, XYSeriesResult
from tascpy.core.step import Step

from ..functional.core import combine as f_combine
from ..functional.core import filters as f_filters
from ..functional.core import math as f_math
from ..functional.core import select as f_select
from ..functional.core import stats as f_stats

if TYPE_CHECKING:
    from .coordinate import CoordinateOps
    from .list import OpsList
    from .load_displacement import LoadDisplacementOps
    from .strain import StrainOps
    from tascpy.domains.coordinate import CoordinateCollection
    from tascpy.domains.load_displacement import LoadDisplacementCollection
    from tascpy.domains.strain import StrainCollection

C_co = TypeVar("C_co", bound=ColumnCollection, covariant=True)

Operand = Union[str, float, int, np.ndarray, Sequence[float]]

_MISSING_TOKENS = {"none", "null", "", "nan", "na"}
_EXPR_FUNCS = {"sin", "cos", "tan", "exp", "log", "sqrt", "abs", "max", "min", "pow", "round", "pi", "e"}


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


def _rebuild(column: Column, values: Any) -> Column:
    """同じ型・属性で値だけ差し替えた列を作る（コンストラクタで値を正規化させる）"""
    return type(column)(column.ch, column.name, column.unit, values, deepcopy(column.metadata))


def _label(operand: Any) -> str:
    s = str(operand)
    return f"({s})" if any(op in s for op in "+-") else s


class CoreOps(Generic[C_co]):
    """ColumnCollection に対するメソッドチェーン用の操作クラス

    各操作は新しいコレクションを生成し、同じ型の操作オブジェクトを返します。
    `end()` でチェーンを終了し、コレクションを取り出します。

    Examples:
        >>> result = col.ops.add("A", "B", result_column="C").filter_by_value("S", "a").end()
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

    def _column_values(self, name: str) -> list:
        if name not in self._c.columns:
            raise KeyError(f"列 '{name}' が存在しません")
        return self._c.columns[name].values

    def _raw(self, operand: Any) -> Any:
        """列名なら列の値配列、配列風なら ndarray、それ以外はそのまま返す"""
        if isinstance(operand, str):
            return np.asarray(self._column_values(operand))
        if isinstance(operand, (list, tuple)):
            return np.asarray(operand)
        return operand

    def _numeric(self, operand: Any) -> Any:
        """列名・配列を欠損 NaN の float 配列に変換する（スカラーはそのまま）"""
        if isinstance(operand, str):
            return to_float_array(self._column_values(operand))
        if isinstance(operand, (list, tuple, np.ndarray)):
            return to_float_array(operand)
        return operand

    def _unit_of(self, operand: Any) -> Optional[str]:
        if isinstance(operand, str) and operand in self._c.columns:
            return getattr(self._c.columns[operand], "unit", None)
        return None

    def _first_unit(self, *operands: Any) -> Optional[str]:
        """列名である最初の引数の単位を返す"""
        for operand in operands:
            if isinstance(operand, str) and operand in self._c.columns:
                return self._unit_of(operand)
        return None

    def _check_columns(self, columns: Optional[List[str]]) -> List[str]:
        names = list(self._c.columns.keys()) if columns is None else list(columns)
        for name in names:
            if name not in self._c.columns:
                raise KeyError(f"列 '{name}' が存在しません")
        return names

    def _with_column(
        self,
        name: str,
        values: Any,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        default_unit: Optional[str] = None,
    ) -> Self:
        """結果を列として追加（同名列があれば値を上書き）した新しいコレクションを返す"""
        if isinstance(values, np.ndarray) and np.issubdtype(values.dtype, np.number) and np.isnan(values).any():
            values = [None if np.isnan(v) else v for v in values]

        result = self._c.clone()
        if name in result.columns:
            column = result.columns[name]
            column.values = values
            if unit is not None:
                column.unit = unit
            if ch is not None:
                column.ch = ch
        else:
            result.add_column(name, detect_column_type(ch, name, unit if unit is not None else default_unit, values))
        return self._next(result)

    def _with_result(self, result: AnalysisResult) -> Self:
        collection = self._c.clone()
        collection.add_result(result)
        return self._next(collection)

    def _with_point(self, name: str, outcome: tuple) -> Self:
        """(is_valid, x, y, info) 形式の計算結果を PointResult として格納する"""
        is_valid, x, y = outcome[0], outcome[1], outcome[2]
        info = dict(outcome[3]) if len(outcome) > 3 else {}
        info["is_valid"] = is_valid
        return self._with_result(PointResult(name=name, x=x, y=y, metadata=info))

    def _with_curve(self, name: str, x: Any, y: Any, metadata: Optional[Dict[str, Any]] = None) -> Self:
        curve = XYSeriesResult(
            name=name,
            x=NumberColumn(ch=None, name=f"{name}_x", unit="", values=x),
            y=NumberColumn(ch=None, name=f"{name}_y", unit="", values=y),
            metadata=metadata or {},
        )
        return self._with_result(curve)

    def _take(self, collection: ColumnCollection, rows: Any) -> ColumnCollection:
        """行インデックスまたはブールマスクで行を抽出した新しいコレクションを返す"""
        selector = np.asarray(rows)
        if selector.dtype != bool:
            selector = selector.astype(int)

        step_values = collection.step.values
        try:
            new_steps = np.asarray(step_values)[selector]
        except IndexError:
            raise IndexError("指定されたインデックスが範囲外です")

        new_columns = {
            name: _rebuild(column, np.asarray(column.values)[selector])
            for name, column in collection.columns.items()
        }

        result = collection.clone()
        result.columns = new_columns
        result.step = Step(values=new_steps.tolist() if isinstance(step_values, list) else new_steps)
        return result

    def _with_rows(self, rows: Any, metadata: Optional[Dict[str, Any]] = None) -> Self:
        result = self._take(self._c, rows)
        if metadata:
            result.metadata.update(metadata)
        return self._next(result)

    def _split(self, row_groups: List[Any]) -> "OpsList[Self]":
        from .list import OpsList

        return OpsList([self._next(self._take(self._c, rows)) for rows in row_groups])

    def _binary(self, name: str, func: Callable, value1: Operand, value2: Operand,
                result_column: Optional[str], unit: Optional[str], ch: Optional[str]) -> Self:
        values = func(self._numeric(value1), self._numeric(value2))
        return self._with_column(
            result_column or f"{_label(value1)}{name}{_label(value2)}",
            values, unit, ch, default_unit=self._first_unit(value1, value2),
        )

    def _unary(self, label: str, values: Any, source: Any,
               result_column: Optional[str], unit: Optional[str], ch: Optional[str]) -> Self:
        return self._with_column(result_column or label, values, unit, ch, default_unit=self._unit_of(source))

    # ── チェーン制御・ドメイン変換 ───────────────────

    def pipe(self, func: Callable[[ColumnCollection], ColumnCollection]) -> Self:
        """コレクションを受け取りコレクションを返す任意の関数を適用します

        Examples:
            >>> col.ops.pipe(lambda c: c.head(3)).end()
        """
        return self._next(func(self._c))

    def debug(self, message: Optional[str] = None) -> Self:
        """コレクションの状態を表示し、自身を返します"""
        if message:
            print(f"DEBUG: {message}")
        print(f"Collection: {self._c}")
        print(f"Domain: {self._c.domain}")
        print(f"Columns: {self._c.columns}")
        print(f"metadata: {self._c.metadata}")
        return self

    def as_domain(self, domain: str, **kwargs: Any) -> "CoreOps[Any]":
        """コレクションを指定ドメインに変換します

        型付きで変換したい場合は `as_load_displacement` / `as_coordinate` / `as_strain` を使用してください。

        Args:
            domain: 変換先のドメイン名（"core", "load_displacement", "coordinate", "strain" など）
            **kwargs: ドメインごとの変換引数
        """
        from tascpy.domains.converters import prepare_for_domain_conversion
        from tascpy.domains.factory import DomainCollectionFactory

        prepared, converted_kwargs = prepare_for_domain_conversion(self._c, target_domain=domain, **kwargs)
        return DomainCollectionFactory.from_collection(prepared, domain, **converted_kwargs).ops

    def as_load_displacement(
        self, load_column: Optional[str] = None, displacement_column: Optional[str] = None
    ) -> "LoadDisplacementOps":
        """荷重-変位ドメインに変換します（列名省略時は推測）"""
        kwargs = {k: v for k, v in {"load_column": load_column, "displacement_column": displacement_column}.items() if v}
        return self.as_domain("load_displacement", **kwargs)  # type: ignore[return-value]

    def as_coordinate(self, coordinates: Optional[Dict[str, Dict[str, float]]] = None, **kwargs: Any) -> "CoordinateOps[CoordinateCollection]":
        """座標ドメインに変換します"""
        if coordinates is not None:
            kwargs["coordinates"] = coordinates
        return self.as_domain("coordinate", **kwargs)  # type: ignore[return-value]

    def as_strain(self, rosettes: Optional[Dict[str, Dict[str, Any]]] = None, **kwargs: Any) -> "StrainOps":
        """ひずみドメインに変換します"""
        if rosettes is not None:
            kwargs["rosettes"] = rosettes
        return self.as_domain("strain", **kwargs)  # type: ignore[return-value]

    # ── 四則演算 ─────────────────────────────────

    def add(self, value1: Operand, value2: Operand, result_column: Optional[str] = None,
            unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """要素ごとの和を新しい列として追加します

        Args:
            value1: 第1引数（列名または数値・配列）
            value2: 第2引数（列名または数値・配列）
            result_column: 結果列名（省略時は "A+B" 形式）。既存列を指定すると上書き
            unit: 結果の単位（省略時は第1引数の列の単位）
            ch: 結果のチャンネル名

        Examples:
            >>> col.ops.add("CH01", "CH02").end()
            >>> col.ops.add("CH01", 10.5, result_column="補正後").end()
        """
        return self._binary("+", f_math.add, value1, value2, result_column, unit, ch)

    def subtract(self, value1: Operand, value2: Operand, result_column: Optional[str] = None,
                 unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """要素ごとの差 (value1 - value2) を新しい列として追加します"""
        return self._binary("-", f_math.subtract, value1, value2, result_column, unit, ch)

    def multiply(self, value1: Operand, value2: Operand, result_column: Optional[str] = None,
                 unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """要素ごとの積を新しい列として追加します"""
        return self._binary("*", f_math.multiply, value1, value2, result_column, unit, ch)

    def divide(self, value1: Operand, value2: Operand, result_column: Optional[str] = None,
               unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """要素ごとの商 (value1 / value2) を新しい列として追加します

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
            values = f_math.divide(numerator, denominator)
        return self._with_column(result_column or f"{_label(value1)}/{_label(value2)}", values, unit, ch,
                                 default_unit=self._first_unit(value1, value2))

    # ── 微分・積分 ───────────────────────────────

    def _strict_pair(self, y_column: Operand, x_column: Operand):
        y, x = self._numeric(y_column), self._numeric(x_column)
        has_missing = np.isnan(y).any() or np.isnan(x).any()
        return y, x, has_missing

    def diff(self, y_column: Operand, x_column: Operand, method: str = "central",
             result_column: Optional[str] = None, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """離散微分 dy/dx を新しい列として追加します（欠損を含む場合は全て欠損）

        Args:
            y_column: Y データの列名
            x_column: X データの列名
            method: 微分手法 ("central", "forward", "backward")
        """
        y, x, has_missing = self._strict_pair(y_column, x_column)
        values = np.full(len(y), np.nan) if has_missing else f_math.diff(y=y, x=x, method=method)
        y_unit, x_unit = self._unit_of(y_column) or "", self._unit_of(x_column) or ""
        return self._with_column(result_column or f"d({y_column})/d({x_column})", values, unit, ch,
                                 default_unit=f"{y_unit}/{x_unit}" if y_unit or x_unit else None)

    def integrate(self, y_column: Operand, x_column: Operand, method: str = "trapezoid", initial_value: float = 0.0,
                  result_column: Optional[str] = None, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """離散積分 ∫y dx を新しい列として追加します（欠損を含む場合は全て欠損）

        Args:
            method: 積分手法 ("trapezoid", "cumulative_sum")
            initial_value: 積分定数
        """
        y, x, has_missing = self._strict_pair(y_column, x_column)
        values = (np.full(len(y), np.nan) if has_missing
                  else f_math.integrate(y=y, x=x, method=method, initial_value=initial_value))
        y_unit, x_unit = self._unit_of(y_column) or "", self._unit_of(x_column) or ""
        return self._with_column(result_column or f"∫{y_column}·d{x_column}", values, unit, ch,
                                 default_unit=f"{y_unit}·{x_unit}" if y_unit or x_unit else None)

    def evaluate(self, expression: str, result_column: Optional[str] = None,
                 unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """列名を変数とした数式を評価し、新しい列として追加します

        Examples:
            >>> col.ops.evaluate("荷重 * 2.0 + 10.0", result_column="補正荷重").end()
        """
        data = {name: column.values for name, column in self._c.columns.items()}
        values = f_math.evaluate_expression(data, expression)
        default_unit = None
        for node in ast.walk(ast.parse(expression, mode="eval")):
            if isinstance(node, ast.Name) and node.id not in _EXPR_FUNCS and node.id in self._c.columns:
                default_unit = self._unit_of(node.id)
                break
        return self._with_column(result_column or "expression_result", values, unit, ch, default_unit=default_unit)

    # ── 単項変換 ─────────────────────────────────

    def log(self, values: Operand, base: float = math.e, result_column: Optional[str] = None,
            unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """対数を新しい列として追加します"""
        prefix = "log" if base == math.e else ("log10" if base == 10 else f"log{base}")
        return self._unary(f"{prefix}({values})", f_math.log(self._numeric(values), base=base),
                           values, result_column, unit, ch)

    def sqrt(self, values: Operand, result_column: Optional[str] = None,
             unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """平方根を新しい列として追加します"""
        return self._unary(f"sqrt({values})", f_math.sqrt(self._numeric(values)), values, result_column, unit, ch)

    def pow(self, values: Operand, exponent: float = 1.0, result_column: Optional[str] = None,
            unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """べき乗を新しい列として追加します"""
        return self._unary(f"{values}^{exponent}", f_math.power(self._numeric(values), exponent=exponent),
                           values, result_column, unit, ch)

    def abs_values(self, values: Operand, result_column: Optional[str] = None,
                   unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """絶対値を新しい列として追加します"""
        return self._unary(f"abs({values})", f_math.abs_values(self._numeric(values)), values, result_column, unit, ch)

    abs = abs_values

    def round_values(self, values: Operand, decimals: int = 0, result_column: Optional[str] = None,
                     unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """四捨五入した値を新しい列として追加します"""
        return self._unary(f"round({values}, {decimals})",
                           f_math.round_values(self._numeric(values), decimals=decimals),
                           values, result_column, unit, ch)

    def normalize(self, values: Operand, method: str = "minmax", result_column: Optional[str] = None,
                  unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """正規化した値を新しい列として追加します

        Args:
            method: 正規化手法 ("minmax", "zscore")
        """
        return self._unary(f"norm_{method}({values})", f_math.normalize(self._numeric(values), method=method),
                           values, result_column, unit, ch)

    def average_across(self, *columns: str, ignore_nan: bool = True, result_column: Optional[str] = None,
                       unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """複数列を行ごとに平均した値を新しい列として追加します

        Examples:
            >>> col.ops.average_across("センサ1", "センサ2", "センサ3", result_column="平均").end()
        """
        arrays = [self._numeric(c) for c in columns]
        values = f_math.average_across(*arrays, ignore_nan=ignore_nan)
        return self._with_column(result_column or f"average_across({','.join(map(str, columns))})", values, unit, ch,
                                 default_unit=self._unit_of(columns[0]) if columns else None)

    # ── 統計 ──────────────────────────────────

    def moving_average(self, column: Operand, window_size: int = 3, edge_handling: str = "asymmetric",
                       result_column: Optional[str] = None, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """移動平均を新しい列として追加します

        Args:
            window_size: ウィンドウサイズ
            edge_handling: 端の処理 ("asymmetric", "symmetric")
        """
        values = f_stats.moving_average(self._numeric(column), window_size=window_size, edge_handling=edge_handling)
        return self._unary(f"ma{window_size}({column})", values, column, result_column, unit, ch)

    def detect_outliers(self, column: Operand, window_size: int = 3, threshold: float = 0.5,
                        edge_handling: str = "asymmetric", min_abs_value: float = 1e-10, scale_factor: float = 1.0,
                        result_column: Optional[str] = None, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """外れ値フラグ（0: 正常, 1: 外れ値）を新しい列として追加します"""
        flags = f_stats.detect_outliers(
            self._numeric(column), window_size=window_size, threshold=threshold, edge_handling=edge_handling,
            min_abs_value=min_abs_value, scale_factor=scale_factor,
        )
        return self._unary(f"outlier({column})", flags, column, result_column, unit, ch)

    def gaussian_filter(self, column: Operand, sigma: float = 1.0, window_size: Optional[int] = None,
                        result_column: Optional[str] = None, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """ガウシアンフィルタで平滑化した値を新しい列として追加します"""
        values = f_stats.gaussian_filter(self._numeric(column), sigma=sigma, window_size=window_size)
        return self._unary(f"gaussian(col={column},sigma={sigma})", values, column, result_column, unit, ch)

    # ── 列の合成 ───────────────────────────────

    def switch_by_step(self, v1: Operand, v2: Operand, threshold: Union[int, float] = 0, compare_mode: str = "value",
                       by_step_value: bool = True, tolerance: Optional[float] = None,
                       result_column: Optional[str] = None, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """ステップ値（またはインデックス）の閾値を境に v1 から v2 へ切り替えた列を追加します"""
        values = f_combine.switch_by_step(
            steps=np.asarray(self._c.step.values), v1=self._raw(v1), v2=self._raw(v2), threshold=threshold,
            compare_mode=compare_mode, by_step_value=by_step_value, tolerance=tolerance,
        )
        return self._unary(f"switch_by_step({v1},{v2})", values, v1, result_column, unit, ch)

    def blend_by_step(self, v1: Operand, v2: Operand, start: Union[int, float] = 0, end: Union[int, float] = 1,
                      compare_mode: str = "value", by_step_value: bool = True, blend_method: str = "linear",
                      tolerance: Optional[float] = None,
                      result_column: Optional[str] = None, unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """ステップ区間 [start, end] で v1 から v2 へ滑らかにブレンドした列を追加します

        Args:
            blend_method: ブレンド手法 ("linear", "smooth", "log", "exp")
        """
        values = f_combine.blend_by_step(
            steps=np.asarray(self._c.step.values), v1=self._raw(v1), v2=self._raw(v2), start=start, end=end,
            compare_mode=compare_mode, by_step_value=by_step_value, blend_method=blend_method, tolerance=tolerance,
        )
        return self._unary(f"blend_by_step({v1},{v2})", values, v1, result_column, unit, ch)

    def sum_columns(self, columns: Optional[List[str]] = None, result_column: Optional[str] = None,
                    unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """複数列の要素ごとの合計を新しい列として追加します（省略時は全列）"""
        names = self._check_columns(columns)
        values = f_combine.sum_columns([np.asarray(self._column_values(n)) for n in names])
        return self._unary(f"sum_columns({','.join(names)})", values, names[0] if names else None,
                           result_column, unit, ch)

    def average_columns(self, columns: Optional[List[str]] = None, result_column: Optional[str] = None,
                        unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """複数列の要素ごとの平均を新しい列として追加します（省略時は全列）"""
        names = self._check_columns(columns)
        values = f_combine.average_columns([np.asarray(self._column_values(n)) for n in names])
        return self._unary(f"average_columns({','.join(names)})", values, names[0] if names else None,
                           result_column, unit, ch)

    def conditional_select(self, v1: Operand, v2: Operand, cond_values: Operand, threshold: Union[int, float] = 0,
                           compare: str = ">", result_column: Optional[str] = None,
                           unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """条件列と閾値の比較結果が真なら v1、偽なら v2 を選んだ列を追加します

        Args:
            compare: 比較演算子 (">", "<", ">=", "<=", "==", "!=")
        """
        values = f_combine.conditional_select(
            v1=self._raw(v1), v2=self._raw(v2), cond_values=self._raw(cond_values),
            threshold=threshold, compare=compare,
        )
        return self._unary(f"conditional_select({v1},{v2})", values, v1, result_column, unit, ch)

    def custom_combine(self, v1: Operand, v2: Operand, combine_func: Callable[[Any, Any], Any],
                       func_name: Optional[str] = None, result_column: Optional[str] = None,
                       unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """任意の関数で 2 列を合成した列を追加します

        Examples:
            >>> col.ops.custom_combine("CH1", "CH2", lambda x, y: x**2 + y**2, func_name="sum_squares").end()
        """
        values = f_combine.custom_combine(v1=self._raw(v1), v2=self._raw(v2), combine_func=combine_func)
        name = func_name or getattr(combine_func, "__name__", "<lambda>")
        if name == "<lambda>":
            name = "custom_combine"
        return self._unary(name, values, v1, result_column, unit, ch)

    # ── 行の抽出・除外 ─────────────────────────────

    def select(self, columns: Optional[List[str]] = None, indices: Optional[List[int]] = None,
               steps: Optional[List[Union[int, float]]] = None, by_step_value: bool = True,
               tolerance: Optional[float] = None) -> Self:
        """列・行インデックス・ステップ値を指定してデータを抽出します

        Args:
            columns: 抽出する列名（省略時は全列）
            indices: 抽出する行インデックス
            steps: 抽出するステップ値（by_step_value=False ならインデックス）
            tolerance: ステップ値一致判定の許容誤差

        Raises:
            KeyError: 存在しない列を指定した場合
            ValueError: indices と steps を同時に指定した場合
        """
        collection = self._c
        if columns is not None:
            names = self._check_columns(columns)
            collection = collection.clone()
            collection.columns = {name: self._c.columns[name].clone() for name in names}

        rows, metadata = f_select.select_indices(
            step_values=np.asarray(collection.step.values), indices=indices, steps=steps,
            by_step_value=by_step_value, tolerance=tolerance,
        )
        result = collection.clone() if rows is None else self._take(collection, rows)
        result.metadata.update(metadata)
        return self._next(result)

    def fetch_near_step(self, column: Operand, target_value: float) -> Self:
        """指定列の値が target_value に最も近い 1 行を抽出します"""
        return self._with_rows(f_select.fetch_near_step(values=self._raw(column), value=target_value))

    def filter_by_value(self, column: str, value: Any, tolerance: Optional[float] = None) -> Self:
        """指定列の値が value と一致する行を抽出します

        Examples:
            >>> col.ops.filter_by_value("状態", "正常").end()
            >>> col.ops.filter_by_value("荷重", 100.0, tolerance=0.5).end()
        """
        return self._with_rows(f_filters.eq(self._raw(column), value=value, tolerance=tolerance))

    def filter_by_condition(self, column: str, condition: Callable[[Any], bool]) -> Self:
        """指定列の各値に condition を適用し、True の行を抽出します

        Examples:
            >>> col.ops.filter_by_condition("荷重", lambda x: x >= 50).end()
        """
        return self._with_rows(f_filters.filter_by_condition(self._raw(column), condition=condition))

    def filter_out_none(self, columns: Optional[List[str]] = None, mode: str = "any") -> Self:
        """欠損値を含む行を除外します

        Args:
            columns: 判定対象の列（省略時は全列）
            mode: "any" はいずれかが欠損、"all" は全てが欠損の行を除外
        """
        data: Dict[str, Any] = {name: np.asarray(self._column_values(name)) for name in self._check_columns(columns)}
        return self._with_rows(f_filters.filter_valid_rows(data, mode=mode))

    def remove_consecutive_duplicates_across(self, columns: Optional[List[str]] = None, dup_type: str = "all") -> Self:
        """連続する重複行を最初の 1 行だけ残して除外します

        Args:
            dup_type: "all" は全列一致、"any" はいずれかの列一致で重複とみなす
        """
        data: Dict[str, Any] = {name: np.asarray(self._column_values(name)) for name in self._check_columns(columns)}
        return self._with_rows(f_filters.duplicated_indices(data, dup_type=dup_type))

    def remove_outliers(self, column: str, window_size: int = 3, threshold: float = 0.5,
                        edge_handling: str = "asymmetric", min_abs_value: float = 1e-10,
                        scale_factor: float = 1.0) -> Self:
        """外れ値と判定された行を除外します"""
        flags = f_stats.detect_outliers(
            np.asarray(self._column_values(column)), window_size=window_size, threshold=threshold,
            edge_handling=edge_handling, min_abs_value=min_abs_value, scale_factor=scale_factor,
        )
        return self._with_rows([i for i, flag in enumerate(flags) if flag == 0])

    def remove_steps(self, steps: List[Any], tolerance: Optional[float] = None) -> Self:
        """指定したステップ値の行を除外します"""
        return self._with_rows(f_filters.remove_steps_mask(
            step_values=np.asarray(self._c.step.values), steps=steps, tolerance=tolerance,
        ))

    # ── 分割 ─────────────────────────────────

    def split_by_integers(self, markers: Union[List[int], np.ndarray]) -> "OpsList[Self]":
        """行ごとの整数マーカーの値ごとにコレクションを分割します

        Examples:
            >>> parts = col.ops.split_by_integers([1, 1, 2, 2, 3])
        """
        return self._split(f_select.split_by_integers(len(self._c), markers))

    def split_at_indices(self, indices: Union[int, List[int]]) -> "OpsList[Self]":
        """指定したインデックスでコレクションを分割します"""
        length = len(self._c)
        return self._split([np.arange(length)[s] for s in f_select.split_at_indices(length, indices)])
