"""座標ドメインの操作"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Self, Tuple, TypeVar

import numpy as np

from tascpy.domains.coordinate import CoordinateCollection

from ..functional.coordinate.interpolation import (
    compute_grid_interpolation_values,
    compute_point_interpolation_values,
    compute_spatial_interpolation_values,
)
from .core import CoreOps

CC_co = TypeVar("CC_co", bound=CoordinateCollection, covariant=True)
CC = TypeVar("CC", bound=CoordinateCollection)


class CoordinateOps(CoreOps[CC_co]):
    """座標付きコレクションの操作（汎用操作も全て利用可能）"""

    def _require_coordinates(self) -> List[str]:
        names = self._c.get_columns_with_coordinates()
        if not names:
            raise ValueError("有効な座標データがありません")
        return names

    def _representative(self, name: str) -> Any:
        column = self._c[name]
        if len(column) == 0:
            return None
        return column.mean() if column.is_numeric else column[0]

    def _sources(self, names: List[str]) -> List[Dict[str, Any]]:
        sources = []
        for name in names:
            value = self._representative(name)
            x, y, z = self._c.get_column_coordinates(name)
            if value is None or x is None or y is None:
                continue
            sources.append({"point": {"x": x, "y": y, "z": z}, "value": value, "col_name": name})
        return sources

    @staticmethod
    def _with_constant(collection: CC, name: str, value: Any, unit: Optional[str],
                       attrs: Dict[str, Any]) -> CC:
        return collection.with_column(name, [value] * len(collection), unit=unit, attrs=attrs)

    def interpolate_at_point(self, x: float, y: float, z: Optional[float] = None,
                             target_columns: Optional[List[str]] = None, method: str = "inverse_distance",
                             power: float = 2.0, result_prefix: str = "interp_") -> Self:
        """座標 (x, y[, z]) での値を各列の代表値（平均）から補間し、"{prefix}{列名}" 列として追加します

        Args:
            target_columns: 補間元の列（省略時は座標を持つ全列）
            method: "inverse_distance", "nearest", "linear"
            power: 逆距離加重法のべき指数
        """
        sources = self._sources(target_columns if target_columns is not None else self._require_coordinates())
        if not sources:
            raise ValueError("補間に使用できる座標付き列がありません")
        is_3d = z is not None
        if is_3d:
            sources = [s for s in sources if s["point"]["z"] is not None]

        values = compute_point_interpolation_values(sources, x, y, z, method, power)
        result = self._c
        for source, value in zip(sources, values):
            name = source["col_name"]
            result = self._with_constant(result, f"{result_prefix}{name}", value, self._unit_of(name), {
                "description": f"Interpolated value at ({x}, {y}{', ' + str(z) if is_3d else ''})",
                "interpolation": {
                    "method": method,
                    "power": power if method == "inverse_distance" else None,
                    "target": {"x": x, "y": y, "z": z if is_3d else None},
                },
            })
        return self._next(result)

    def interpolate_grid(self, x_range: Tuple[float, float], y_range: Tuple[float, float],
                         grid_size: Tuple[int, int] = (10, 10), target_column: Optional[str] = None,
                         method: str = "inverse_distance", power: float = 2.0, result_prefix: str = "grid_") -> Self:
        """矩形領域のグリッド上で補間し、"{prefix}{列名}_grid" 列とメタデータ analysis.grid_interpolation に格納します"""
        target_column = target_column or self._require_coordinates()[0]
        if target_column not in self._c:
            raise ValueError(f"列 '{target_column}' が見つかりません")
        if len(self._c) == 0:
            raise ValueError(f"列 '{target_column}' に値がありません")
        sources = self._sources([target_column])
        if not sources:
            raise ValueError(f"列 '{target_column}' に座標情報がありません")

        nx, ny = grid_size
        grid = compute_grid_interpolation_values(
            sources[0], np.linspace(x_range[0], x_range[1], nx), np.linspace(y_range[0], y_range[1], ny), method, power,
        )

        analysis = dict(self._c.metadata.get("analysis", {}))
        analysis["grid_interpolation"] = {
            "x_range": x_range, "y_range": y_range, "grid_size": grid_size,
            "method": method, "target_column": target_column,
        }
        name = f"{result_prefix}{target_column}_grid"
        result = self._with_constant(
            self._c.with_metadata(analysis=analysis), name,
            np.array2string(grid, precision=4, suppress_small=True), None, {
                "description": f"Grid interpolation of {target_column}",
                "grid": {
                    "x_min": float(x_range[0]), "x_max": float(x_range[1]),
                    "y_min": float(y_range[0]), "y_max": float(y_range[1]),
                    "nx": nx, "ny": ny,
                },
            })
        return self._next(result)

    def spatial_interpolation_to_points(self, source_columns: Optional[List[str]] = None,
                                        target_columns: Optional[List[str]] = None,
                                        method: str = "inverse_distance", power: float = 2.0,
                                        result_prefix: str = "interp_") -> Self:
        """補間元の列の値からターゲット列の座標位置の値を補間し、"{prefix}{ターゲット列}" 列として追加します"""
        with_coords = self._require_coordinates()
        source_columns = with_coords if source_columns is None else source_columns
        if target_columns is None:
            target_columns = [c for c in with_coords if c not in source_columns]
        if not source_columns:
            raise ValueError("補間元の座標付き列がありません")
        if not target_columns:
            raise ValueError("補間先の座標付き列がありません")

        sources = self._sources(source_columns)
        is_3d = bool(sources) and all(s["point"]["z"] is not None for s in sources)

        targets, coords = [], []
        for name in target_columns:
            tx, ty, tz = self._c.get_column_coordinates(name)
            if tx is None or ty is None:
                continue
            targets.append(name)
            coords.append({"x": tx, "y": ty, "z": tz if tz is not None and is_3d else None})

        values = compute_spatial_interpolation_values(sources, coords, is_3d, method, power)
        result = self._c
        for name, value in zip(targets, values):
            result = self._with_constant(result, f"{result_prefix}{name}", value, None, {
                "description": f"Interpolated value at {name} position",
                "interpolation": {
                    "method": method,
                    "power": power if method == "inverse_distance" else None,
                    "source_columns": source_columns,
                    "target_column": name,
                },
            })
        return self._next(result)
