from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Self, Tuple, Union

import numpy as np

from tascpy.core.collection import ColumnCollection
from tascpy.numeric.spatial import euclidean_distance, find_nearest_neighbors_logic, simple_kmeans

if TYPE_CHECKING:
    from ..analytics.ops import CoordinateOps
    from ..visualization.plotters.coordinate.plotter import CoordinatePlotter

COORDINATES_KEY = "coordinates"
"""座標を格納する ColumnMeta.attrs のキー"""

Coordinates = Union[Mapping[str, Mapping[str, Optional[float]]], str, Path]


def load_coordinates(path: Union[str, Path]) -> Dict[str, Dict[str, Optional[float]]]:
    """座標ファイルを読み込む

    JSON は {列名: {"x": .., "y": .., "z": ..}}、CSV は column, x, y, z 列（大文字小文字は区別しない）の形式です。
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"座標ファイルが見つかりません: {path}")
    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    if suffix != ".csv":
        raise ValueError(f"サポートされていないファイル形式です: {suffix}")

    result: Dict[str, Dict[str, Optional[float]]] = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = {h.lower(): h for h in reader.fieldnames or []}
        if "column" not in header:
            return result
        for row in reader:
            coords: Dict[str, Optional[float]] = {}
            for axis in ("x", "y", "z"):
                raw = row.get(header[axis]) if axis in header else None
                if raw:
                    try:
                        coords[axis] = float(raw)
                    except ValueError:
                        coords[axis] = None
            result[row[header["column"]]] = coords
    return result


class CoordinateCollection(ColumnCollection):
    """列ごとに座標 (x, y, z) を持つコレクション

    座標は各列の `ColumnMeta.attrs["coordinates"]` に格納されるため、列の改名・選択に追従します。

    Examples:
        >>> col = CoordinateCollection({"CH1": [100.0]}, coordinates={"CH1": {"x": 10.0, "y": 20.0}})
        >>> col.get_column_coordinates("CH1")
        (10.0, 20.0, None)
    """

    domain = "coordinate"

    def __init__(self, columns: Optional[Mapping[str, Any]] = None, *,
                 coordinates: Optional[Coordinates] = None, **kwargs: Any) -> None:
        super().__init__(columns, **kwargs)
        configured = self._with_coordinate_map(coordinates)
        self._set(configured._df, configured._meta, configured._metadata, configured._results)

    @classmethod
    def from_collection(cls, collection: ColumnCollection, *, coordinates: Optional[Coordinates] = None) -> Self:
        return collection._as_class(cls)._with_coordinate_map(coordinates)

    def _with_coordinate_map(self, coordinates: Optional[Coordinates]) -> Self:
        if coordinates is None:
            return self
        if isinstance(coordinates, (str, Path)):
            coordinates = load_coordinates(coordinates)
        new = self
        for name, xyz in coordinates.items():
            if name in new:
                new = new.with_coordinates(name, x=xyz.get("x"), y=xyz.get("y"), z=xyz.get("z"))
        return new

    @property
    def ops(self) -> "CoordinateOps[Self]":
        """座標ドメインの操作オブジェクト"""
        from ..analytics.ops import CoordinateOps

        return CoordinateOps(self)

    @property
    def plot(self) -> "CoordinatePlotter":
        """座標データのプロッター"""
        from ..visualization.plotters.coordinate.plotter import CoordinatePlotter

        return CoordinatePlotter(self)

    # ── 座標 ──────────────────────────────────

    def with_coordinates(self, column_name: str, x: Optional[float] = None, y: Optional[float] = None,
                         z: Optional[float] = None) -> Self:
        """列の座標を設定する（None の軸は既存の値を残す）"""
        if column_name not in self:
            raise ValueError(f"カラム '{column_name}' が見つかりません")
        coords = dict(self.meta[column_name].attrs.get(COORDINATES_KEY, {"x": None, "y": None, "z": None}))
        coords.update({k: v for k, v in {"x": x, "y": y, "z": z}.items() if v is not None})
        return self.with_attrs(column_name, **{COORDINATES_KEY: coords})

    def get_column_coordinates(self, column_name: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """列の座標 (x, y, z)（未設定の軸は None）"""
        if column_name not in self:
            raise ValueError(f"カラム '{column_name}' が見つかりません")
        coords = self.meta[column_name].attrs.get(COORDINATES_KEY, {})
        return coords.get("x"), coords.get("y"), coords.get("z")

    def get_columns_with_coordinates(self) -> List[str]:
        """いずれかの軸の座標が設定されている列名"""
        return [name for name in self.columns if any(v is not None for v in self.get_column_coordinates(name))]

    def get_coordinate_matrix(self, columns: Optional[List[str]] = None,
                              include_z: bool = False) -> Tuple[np.ndarray, List[str]]:
        """座標の行列 (N x 2 または N x 3) と、対象になった列名

        x, y（include_z なら z も）が揃っていない列はスキップします。

        Raises:
            ValueError: 有効な座標が1つもない場合
        """
        rows, valid = [], []
        for name in self.get_columns_with_coordinates() if columns is None else columns:
            if name not in self:
                continue
            x, y, z = self.get_column_coordinates(name)
            if x is None or y is None or (include_z and z is None):
                continue
            rows.append([x, y, z] if include_z else [x, y])
            valid.append(name)
        if not rows:
            raise ValueError("有効な座標データが見つかりません")
        return np.array(rows), valid

    def calculate_distance(self, column1: str, column2: str) -> float:
        """2列の座標間のユークリッド距離（どちらかに z がなければ 2D）"""
        x1, y1, z1 = self.get_column_coordinates(column1)
        x2, y2, z2 = self.get_column_coordinates(column2)
        if x1 is None or y1 is None or x2 is None or y2 is None:
            raise ValueError("距離計算に必要な座標情報が不足しています")
        if z1 is None or z2 is None:
            return euclidean_distance([x1, y1], [x2, y2])
        return euclidean_distance([x1, y1, z1], [x2, y2, z2])

    def _with_domain_metadata(self, key: str, value: Dict[str, Any]) -> Self:
        domain_md = dict(self.metadata.get("coordinate_domain", {}))
        domain_md[key] = value
        return self.with_metadata(coordinate_domain=domain_md)

    def find_nearest_neighbors(self, column: str, n_neighbors: int = 3,
                               result_column: Optional[str] = None) -> Self:
        """座標空間で column に最も近い n 列を探す

        結果はメタデータ coordinate_domain.nearest_neighbors_{column} と、
        attrs に結果を持つ列 "{column}_neighbors"（値は 1.0）に格納します。
        """
        if column not in self:
            raise ValueError(f"指定されたカラム '{column}' が見つかりません。")
        valid = self.get_columns_with_coordinates()
        if len(valid) <= 1:
            raise ValueError("十分な数の座標データがありません。")
        if column not in valid:
            raise ValueError(f"カラム '{column}' には有効な座標が設定されていません。")

        candidates = [(name, self.calculate_distance(column, name)) for name in valid if name != column]
        neighbors = find_nearest_neighbors_logic(candidates, n_neighbors)
        info = {
            "operation": "find_nearest_neighbors",
            "base_column": column,
            "neighbors": [name for name, _ in neighbors],
            "distances": [float(d) for _, d in neighbors],
        }
        new = self.with_column(result_column or f"{column}_neighbors", np.ones(len(self)), unit="", attrs=info)
        return new._with_domain_metadata(f"nearest_neighbors_{column}", info)

    def spatial_clustering(self, n_clusters: int = 2, columns: Optional[List[str]] = None,
                           result_column: str = "cluster", algorithm: str = "kmeans") -> Self:
        """座標に基づいて列をクラスタリングする

        各列の attrs に "cluster_id" を付与し、結果をメタデータ coordinate_domain.clustering_result と
        attrs に結果を持つ列 result_column（値は欠損）に格納します。
        """
        matrix, valid = self.get_coordinate_matrix(columns, include_z=True)
        if len(valid) < n_clusters:
            raise ValueError(f"クラスタ数({n_clusters})が有効な座標データの数({len(valid)})を上回っています。")
        if algorithm.lower() != "kmeans":
            raise NotImplementedError(f"アルゴリズム '{algorithm}' は未実装です。")

        labels = [int(label) for label in simple_kmeans(matrix, n_clusters)]
        info = {
            "operation": "spatial_clustering",
            "algorithm": algorithm,
            "n_clusters": n_clusters,
            "assignments": dict(zip(valid, labels)),
        }
        new = self
        for name, label in zip(valid, labels):
            new = new.with_attrs(name, cluster_id=label)
        new = new.with_column(result_column, np.full(len(self), np.nan), unit="", attrs=info)
        return new._with_domain_metadata("clustering_result", info)
