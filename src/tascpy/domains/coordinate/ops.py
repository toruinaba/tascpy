"""座標ドメインの操作"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Self, Tuple, TypeVar

import numpy as np

from tascpy.core.ops import CoreOps
from tascpy.core.result import GridResult
from tascpy.numeric.spatial import interpolate, kmeans

from .collection import CoordinateCollection

CC = TypeVar("CC", bound=CoordinateCollection)
CC_co = TypeVar("CC_co", bound=CoordinateCollection, covariant=True)


def _with_domain_metadata(collection: CC, key: str, value: Dict[str, Any]) -> CC:
    domain_md = dict(collection.metadata.get("coordinate_domain", {}))
    domain_md[key] = value
    return collection.with_metadata(coordinate_domain=domain_md)


class CoordinateOps(CoreOps[CC_co]):
    """座標付きコレクションの操作（汎用操作も全て利用可能）

    補間は各行（時刻）ごとに、座標を持つ数値列の値から計算します。
    """

    def _require_coordinates(self) -> List[str]:
        names = self._c.get_columns_with_coordinates()
        if not names:
            raise ValueError("有効な座標データがありません")
        return names

    def _sources(self, names: Optional[List[str]], use_z: bool) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """補間元の (列名, 座標 (N, D), 値 (N, 行数))。座標が揃わない列・数値でない列は除く"""
        used, points = [], []
        for name in self._require_coordinates() if names is None else self._check_columns(names):
            x, y, z = self._c.get_column_coordinates(name)
            if x is None or y is None or (use_z and z is None) or not self._c[name].is_numeric:
                continue
            used.append(name)
            points.append([x, y, z] if use_z else [x, y])
        if not used:
            raise ValueError("補間に使用できる座標付きの数値列がありません")
        values = np.vstack([self._c[name].values for name in used])
        return used, np.array(points, dtype=float), values

    def _common_unit(self, names: List[str]) -> Optional[str]:
        units = {self._unit_of(name) for name in names}
        return units.pop() if len(units) == 1 else None

    @staticmethod
    def _info(method: str, power: float, sources: List[str], **extra: Any) -> Dict[str, Any]:
        return {"method": method, "power": power if method == "inverse_distance" else None,
                "source_columns": sources, **extra}

    def interpolate_at_point(self, x: float, y: float, z: Optional[float] = None,
                             source_columns: Optional[List[str]] = None, method: str = "inverse_distance",
                             power: float = 2.0, result_column: Optional[str] = None,
                             unit: Optional[str] = None) -> Self:
        """座標 (x, y[, z]) での値を行ごとに補間した列を追加します

        追加した列には補間点の座標が設定されます。単位は、補間元の単位がすべて同じならその単位、
        異なれば None です。z を指定した場合は z 座標を持つ列だけを補間元にします。

        Args:
            source_columns: 補間元の列（省略時は座標を持つ全列）
            method: "inverse_distance" または "nearest"
            power: 逆距離加重のべき指数
            result_column: 結果列名（省略時は "interp(x, y[, z])"）

        Examples:
            >>> center = coord.ops.interpolate_at_point(5.0, 0.0, source_columns=["CH1", "CH2"], result_column="center").end()
            >>> center["center"].values, center.get_column_coordinates("center")
            (array([  0.,  75., 150., 225., 300., 375.]), (5.0, 0.0, None))
        """
        use_z = z is not None
        names, points, values = self._sources(source_columns, use_z)
        target = [x, y, z] if use_z else [x, y]
        result = interpolate(points, values, target, method=method, power=power)

        name = result_column or f"interp({', '.join(f'{v:g}' for v in target)})"
        collection = self._c.with_column(
            name, result, unit=unit if unit is not None else self._common_unit(names),
            attrs={"interpolation": self._info(method, power, names)},
        ).with_coordinates(name, x, y, z)
        return self._next(collection)

    def spatial_interpolation_to_points(self, source_columns: Optional[List[str]] = None,
                                        target_columns: Optional[List[str]] = None,
                                        method: str = "inverse_distance", power: float = 2.0,
                                        result_prefix: str = "interp_") -> Self:
        """補間先の列の座標位置での値を、補間元の列から行ごとに補間して "{prefix}{補間先の列名}" 列として追加します

        補間元と補間先がすべて z 座標を持つ場合は 3 次元、それ以外は x, y で補間します。

        Args:
            source_columns: 補間元の列（省略時は座標を持つ全列）
            target_columns: 補間先の列（省略時は補間元以外の座標を持つ列）
        """
        with_coords = self._require_coordinates()
        source_names = with_coords if source_columns is None else source_columns
        target_names = ([c for c in with_coords if c not in source_names]
                        if target_columns is None else self._check_columns(target_columns))
        if not target_names:
            raise ValueError("補間先の座標付き列がありません")

        target_coords = {name: self._c.get_column_coordinates(name) for name in target_names}
        target_coords = {n: c for n, c in target_coords.items() if c[0] is not None and c[1] is not None}
        use_z = (all(c[2] is not None for c in target_coords.values())
                 and all(self._c.get_column_coordinates(n)[2] is not None for n in source_names))
        names, points, values = self._sources(source_names, use_z)
        targets = np.array([c if use_z else c[:2] for c in target_coords.values()], dtype=float)
        results = interpolate(points, values, targets, method=method, power=power)

        collection = self._c
        unit = self._common_unit(names)
        for (target, (tx, ty, tz)), result in zip(target_coords.items(), results):
            name = f"{result_prefix}{target}"
            collection = collection.with_column(
                name, result, unit=unit, attrs={"interpolation": self._info(method, power, names, target_column=target)},
            ).with_coordinates(name, tx, ty, tz)
        return self._next(collection)

    def interpolate_grid(self, x_range: Tuple[float, float], y_range: Tuple[float, float],
                         grid_size: Tuple[int, int] = (10, 10), source_columns: Optional[List[str]] = None,
                         row: int = 0, method: str = "inverse_distance", power: float = 2.0,
                         result_name: str = "grid") -> Self:
        """指定した行の値を矩形グリッド上に補間し、結果 result_name (GridResult) に格納します

        Args:
            x_range: X の範囲 (最小, 最大)
            y_range: Y の範囲 (最小, 最大)
            grid_size: グリッドの点数 (nx, ny)
            source_columns: 補間元の列（省略時は座標を持つ全列）
            row: 補間する行のインデックス（負の値は末尾から）

        Examples:
            >>> grid = coord.ops.interpolate_grid((0, 10), (0, 10), (20, 20), row=-1).end().results["grid"]
            >>> grid.values.shape
            (20, 20)
        """
        n = len(self._c)
        if not -n <= row < n:
            raise IndexError(f"行インデックス {row} が範囲外です（行数 {n}）")
        names, points, values = self._sources(source_columns, use_z=False)
        nx, ny = grid_size
        xs, ys = np.linspace(*x_range, nx), np.linspace(*y_range, ny)
        gx, gy = np.meshgrid(xs, ys)
        grid = interpolate(points, values[:, row], np.column_stack([gx.ravel(), gy.ravel()]),
                           method=method, power=power).reshape(ny, nx)
        step = self._c.step[row]
        return self._with_result(GridResult(
            result_name, xs, ys, grid, unit=self._common_unit(names),
            metadata=self._info(method, power, names, row=row, step=step.item() if hasattr(step, "item") else step),
        ))

    # ── 近傍・クラスタリング ─────────────────────

    def find_nearest_neighbors(self, column: str, n_neighbors: int = 3,
                               result_column: Optional[str] = None) -> Self:
        """座標空間で column に最も近い n 列を探す

        結果はメタデータ coordinate_domain.nearest_neighbors_{column} と、
        attrs に結果を持つ列 "{column}_neighbors"（値は 1.0）に格納します。
        """
        if column not in self._c:
            raise ValueError(f"指定されたカラム '{column}' が見つかりません。")
        valid = self._c.get_columns_with_coordinates()
        if len(valid) <= 1:
            raise ValueError("十分な数の座標データがありません。")
        if column not in valid:
            raise ValueError(f"カラム '{column}' には有効な座標が設定されていません。")

        candidates = [(name, self._c.calculate_distance(column, name)) for name in valid if name != column]
        neighbors = sorted((c for c in candidates if not np.isnan(c[1])), key=lambda c: c[1])[:n_neighbors]
        info = {
            "operation": "find_nearest_neighbors",
            "base_column": column,
            "neighbors": [name for name, _ in neighbors],
            "distances": [float(d) for _, d in neighbors],
        }
        new = self._c.with_column(result_column or f"{column}_neighbors", np.ones(len(self._c)), unit="", attrs=info)
        return self._next(_with_domain_metadata(new, f"nearest_neighbors_{column}", info))

    def spatial_clustering(self, n_clusters: int = 2, columns: Optional[List[str]] = None,
                           result_column: str = "cluster", algorithm: str = "kmeans") -> Self:
        """座標に基づいて列をクラスタリングする

        各列の attrs に "cluster_id" を付与し、結果をメタデータ coordinate_domain.clustering_result と
        attrs に結果を持つ列 result_column（値は欠損）に格納します。
        """
        matrix, valid = self._c.get_coordinate_matrix(columns, include_z=True)
        if len(valid) < n_clusters:
            raise ValueError(f"クラスタ数({n_clusters})が有効な座標データの数({len(valid)})を上回っています。")
        if algorithm.lower() != "kmeans":
            raise NotImplementedError(f"アルゴリズム '{algorithm}' は未実装です。")

        labels = [int(label) for label in kmeans(matrix, n_clusters)]
        info = {
            "operation": "spatial_clustering",
            "algorithm": algorithm,
            "n_clusters": n_clusters,
            "assignments": dict(zip(valid, labels)),
        }
        new = self._c
        for name, label in zip(valid, labels):
            new = new.with_attrs(name, cluster_id=label)
        new = new.with_column(result_column, np.full(len(self._c), np.nan), unit="", attrs=info)
        return self._next(_with_domain_metadata(new, "clustering_result", info))
