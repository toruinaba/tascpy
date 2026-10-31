"""座標ドメインのコレクションクラスのテスト"""

import json

import pytest

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.domains.coordinate.collection import COORDINATES_KEY
from tascpy.domains import as_coordinate


class TestCoordinateCollection:
    def setup_method(self):
        self.steps = list(range(5))
        self.values1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.values2 = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.column1 = Column("sensor1", self.values1, unit="m")
        self.column2 = Column("sensor2", self.values2, unit="m")
        self.columns = {"sensor1": self.column1, "sensor2": self.column2}
        self.collection = ColumnCollection(self.columns, step=self.steps)

    def _coord(self, columns=None, **kwargs):
        return CoordinateCollection(columns or self.columns, step=self.steps, **kwargs)

    def test_initialization(self):
        coll = self._coord()
        assert coll.domain == "coordinate"
        for name in coll.columns:
            assert coll.get_column_coordinates(name) == (None, None, None)
        assert coll["sensor1"].unit == "m"

    def test_from_collection(self):
        coll = self.collection.ops.end_as(as_coordinate)
        assert isinstance(coll, CoordinateCollection)
        assert coll["sensor1"].to_list() == self.values1

    def test_from_collection_with_coordinates(self):
        coll = self.collection.ops.end_as(as_coordinate, coordinates={"sensor1": {"x": 1.0, "y": 2.0}})
        assert coll.get_column_coordinates("sensor1") == (1.0, 2.0, None)

    def test_set_get_coordinates(self):
        coll = self._coord().with_coordinates("sensor1", x=1.5, y=2.5, z=3.5)
        assert coll.get_column_coordinates("sensor1") == (1.5, 2.5, 3.5)

        coll = coll.with_coordinates("sensor2", x=4.5, z=6.5)
        x, y, z = coll.get_column_coordinates("sensor2")
        assert x == 4.5
        assert y is None
        assert z == 6.5

    def test_with_coordinates_returns_new_collection(self):
        original = self._coord()
        updated = original.with_coordinates("sensor1", x=1.0)
        assert original.get_column_coordinates("sensor1") == (None, None, None)
        assert updated.get_column_coordinates("sensor1")[0] == 1.0

    def test_with_coordinates_keeps_existing_axes(self):
        coll = self._coord().with_coordinates("sensor1", x=1.0, y=2.0).with_coordinates("sensor1", x=10.0)
        assert coll.get_column_coordinates("sensor1") == (10.0, 2.0, None)

    def test_coordinates_stored_in_attrs(self):
        coll = self._coord(coordinates={"sensor1": {"x": 10.0, "y": 20.0, "z": 30.0}})
        assert coll.meta["sensor1"].attrs[COORDINATES_KEY]["x"] == 10.0

    def test_coordinates_follow_rename_and_select(self):
        coll = self._coord(coordinates={"sensor1": {"x": 1.0, "y": 2.0}})
        renamed = coll.rename({"sensor1": "s1"})
        assert isinstance(renamed, CoordinateCollection)
        assert renamed.get_column_coordinates("s1") == (1.0, 2.0, None)
        assert coll.select(["sensor1"]).get_columns_with_coordinates() == ["sensor1"]

    def test_get_columns_with_coordinates(self):
        columns = {**self.columns, "sensor3": Column("sensor3", [0.0] * 5, unit="m")}
        coll = self._coord(columns)
        assert coll.get_columns_with_coordinates() == []

        coll = coll.with_coordinates("sensor1", x=1.0).with_coordinates("sensor3", y=3.0)
        with_coords = coll.get_columns_with_coordinates()
        assert len(with_coords) == 2
        assert "sensor1" in with_coords
        assert "sensor3" in with_coords
        assert "sensor2" not in with_coords

    def test_distance(self):
        coll = self._coord().with_coordinates("sensor1", x=0.0, y=0.0).with_coordinates("sensor2", x=3.0, y=4.0)
        assert coll.distance("sensor1", "sensor2") == 5.0

        coll = coll.with_coordinates("sensor1", z=0.0).with_coordinates("sensor2", z=12.0)
        assert coll.distance("sensor1", "sensor2") == 13.0

    def test_missing_column(self):
        coll = self._coord()
        with pytest.raises(ValueError) as exc_info:
            coll.with_coordinates("sensor3", x=1.0)
        assert "見つかりません" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            coll.get_column_coordinates("sensor3")
        assert "見つかりません" in str(exc_info.value)

    def test_distance_error(self):
        coll = self._coord()
        with pytest.raises(ValueError) as exc_info:
            coll.distance("sensor1", "sensor2")
        assert "座標情報が不足" in str(exc_info.value)

        coll = coll.with_coordinates("sensor1", x=1.0, y=1.0).with_coordinates("sensor2", x=2.0)
        with pytest.raises(ValueError) as exc_info:
            coll.distance("sensor1", "sensor2")
        assert "座標情報が不足" in str(exc_info.value)

    def test_initialization_with_coordinates(self):
        coordinates = {
            "sensor1": {"x": 1.0, "y": 2.0, "z": 3.0},
            "sensor2": {"x": 4.0, "y": 5.0},
        }
        coll = self._coord(coordinates=coordinates)
        assert coll.get_column_coordinates("sensor1") == (1.0, 2.0, 3.0)
        assert coll.get_column_coordinates("sensor2") == (4.0, 5.0, None)
        assert set(coll.get_columns_with_coordinates()) == {"sensor1", "sensor2"}

    def test_initialization_ignores_unknown_columns(self):
        coll = self._coord(coordinates={"unknown": {"x": 1.0}})
        assert coll.get_columns_with_coordinates() == []

    def test_coordinates_from_json_file(self, tmp_path):
        path = tmp_path / "coords.json"
        path.write_text(json.dumps({"sensor1": {"x": 5.0, "y": 6.0, "z": 7.0}}), encoding="utf-8")
        coll = self._coord(coordinates=str(path))
        assert coll.get_column_coordinates("sensor1") == (5.0, 6.0, 7.0)

    def test_coordinates_from_csv_file(self, tmp_path):
        path = tmp_path / "coords.csv"
        path.write_text("Column,X,Y,Z\nsensor1,1,2,3\nsensor2,4,5,\n", encoding="utf-8")
        coll = self._coord(coordinates=path)
        assert coll.get_column_coordinates("sensor1") == (1.0, 2.0, 3.0)
        assert coll.get_column_coordinates("sensor2") == (4.0, 5.0, None)

    def test_coordinates_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            self._coord(coordinates=str(tmp_path / "missing.json"))


def test_nearest_neighbors():
    """基準列からの距離が近い順に近傍列を返す"""
    collection = CoordinateCollection(
        {name: [1.0, 2.0] for name in ["A", "B", "C", "D"]},
        step=[1, 2],
        coordinates={
            "A": {"x": 0.0, "y": 0.0},
            "B": {"x": 3.0, "y": 0.0},
            "C": {"x": 1.0, "y": 0.0},
            "D": {"x": 0.0, "y": 2.0},
        },
    )
    neighbors = collection.ops.nearest_neighbors("A", n_neighbors=2)
    assert neighbors == {"C": 1.0, "D": 2.0}
    assert list(neighbors) == ["C", "D"]


def test_clusters():
    collection = CoordinateCollection(
        {name: [1.0, 2.0] for name in ["A", "B", "C", "D"]},
        step=[1, 2],
        coordinates={
            "A": {"x": 0.0, "y": 0.0, "z": 0.0},
            "B": {"x": 0.1, "y": 0.0, "z": 0.0},
            "C": {"x": 10.0, "y": 10.0, "z": 0.0},
            "D": {"x": 10.1, "y": 10.0, "z": 0.0},
        },
    )
    assignments = collection.ops.clusters(n_clusters=2)
    assert set(assignments) == {"A", "B", "C", "D"}
    assert assignments["A"] == assignments["B"]
    assert assignments["C"] == assignments["D"]
    assert assignments["A"] != assignments["C"]
