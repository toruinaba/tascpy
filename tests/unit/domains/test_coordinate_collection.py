"""座標ドメインのコレクションクラスのテスト"""

import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection


class TestCoordinateCollection:
    """座標ドメインのコレクションクラスのテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # 基本的なデータを作成
        self.steps = list(range(5))
        self.values1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.values2 = [10.0, 20.0, 30.0, 40.0, 50.0]

        # Columnオブジェクトを作成（単位を追加）
        self.column1 = Column(ch=None, name="sensor1", unit="m", values=self.values1)
        self.column2 = Column(ch=None, name="sensor2", unit="m", values=self.values2)

        # 基本のコレクションを作成
        self.collection = ColumnCollection(
            self.steps, {"sensor1": self.column1, "sensor2": self.column2}
        )

    def test_initialization(self):
        """基本的な初期化のテスト"""
        # CoordinateCollectionを直接初期化
        coord_collection = CoordinateCollection(
            self.steps, {"sensor1": self.column1, "sensor2": self.column2}
        )

        # プロパティが正しく設定されていることを確認
        assert coord_collection.coordinate_metadata_key == "coordinates"
        assert coord_collection.domain == "coordinate"

        # 各列にメタデータが初期化されていることを確認
        for col_name in coord_collection.columns:
            assert "coordinates" in coord_collection.columns[col_name].metadata
            coords = coord_collection.columns[col_name].metadata["coordinates"]
            assert coords["x"] is None
            assert coords["y"] is None
            assert coords["z"] is None

    def test_initialization_custom_metadata_key(self):
        """カスタムメタデータキーでの初期化テスト"""
        # カスタムメタデータキーで初期化
        coord_collection = CoordinateCollection(
            self.steps,
            {"sensor1": self.column1, "sensor2": self.column2},
            coordinate_metadata_key="position",
        )

        # カスタムキーが正しく設定されていることを確認
        assert coord_collection.coordinate_metadata_key == "position"

        # 各列のメタデータが正しいキーで初期化されていることを確認
        for col_name in coord_collection.columns:
            assert "position" in coord_collection.columns[col_name].metadata

    def test_from_collection(self):
        """通常のコレクションからの変換テスト"""
        # ops.as_domain()を使用してドメインコレクションに変換
        coord_collection = self.collection.ops.as_domain("coordinate").end()

        # 型と内容を確認
        assert isinstance(coord_collection, CoordinateCollection)
        assert coord_collection.coordinate_metadata_key == "coordinates"
        assert list(coord_collection["sensor1"].values) == self.values1

    def test_set_get_coordinates(self):
        """座標の設定と取得のテスト"""
        # CoordinateCollectionを初期化
        coord_collection = CoordinateCollection(
            self.steps, {"sensor1": self.column1, "sensor2": self.column2}
        )

        # sensor1に座標を設定
        coord_collection.set_column_coordinates("sensor1", x=1.5, y=2.5, z=3.5)

        # 座標が正しく設定されたか確認
        x, y, z = coord_collection.get_column_coordinates("sensor1")
        assert x == 1.5
        assert y == 2.5
        assert z == 3.5

        # 部分的な座標設定のテスト
        coord_collection.set_column_coordinates("sensor2", x=4.5, z=6.5)
        x, y, z = coord_collection.get_column_coordinates("sensor2")
        assert x == 4.5
        assert y is None
        assert z == 6.5

    def test_get_columns_with_coordinates(self):
        """座標が設定されている列の取得テスト"""
        # 追加のColumnオブジェクトを作成
        column3 = Column(ch=None, name="sensor3", unit="m", values=[0.0] * 5)

        coord_collection = CoordinateCollection(
            self.steps,
            {"sensor1": self.column1, "sensor2": self.column2, "sensor3": column3},
        )

        # 初期状態では座標が設定されている列はない
        assert len(coord_collection.get_columns_with_coordinates()) == 0

        # sensor1とsensor3に座標を設定
        coord_collection.set_column_coordinates("sensor1", x=1.0)
        coord_collection.set_column_coordinates("sensor3", y=3.0)

        # 座標が設定されている列を取得
        columns_with_coords = coord_collection.get_columns_with_coordinates()
        assert len(columns_with_coords) == 2
        assert "sensor1" in columns_with_coords
        assert "sensor3" in columns_with_coords
        assert "sensor2" not in columns_with_coords

    def test_calculate_distance(self):
        """距離計算のテスト"""
        coord_collection = CoordinateCollection(
            self.steps, {"sensor1": self.column1, "sensor2": self.column2}
        )

        # 2D座標を設定
        coord_collection.set_column_coordinates("sensor1", x=0.0, y=0.0)
        coord_collection.set_column_coordinates("sensor2", x=3.0, y=4.0)

        # 2D距離の計算（3-4-5の三角形）
        distance_2d = coord_collection.calculate_distance("sensor1", "sensor2")
        assert distance_2d == 5.0

        # 3D座標を設定
        coord_collection.set_column_coordinates("sensor1", z=0.0)
        coord_collection.set_column_coordinates("sensor2", z=12.0)

        # 3D距離の計算
        distance_3d = coord_collection.calculate_distance("sensor1", "sensor2")
        assert distance_3d == 13.0

    def test_clone(self):
        """クローン操作のテスト"""
        # 元のCoordinateCollectionを作成して座標を設定
        original = CoordinateCollection(
            self.steps, {"sensor1": self.column1, "sensor2": self.column2}
        )
        original.set_column_coordinates("sensor1", x=1.0, y=2.0, z=3.0)

        # クローンを作成
        cloned = original.clone()

        # クローンがCoordinateCollectionであることを確認
        assert isinstance(cloned, CoordinateCollection)

        # ドメイン固有のプロパティが保持されていることを確認
        assert cloned.coordinate_metadata_key == original.coordinate_metadata_key

        # 座標データが同じであることを確認
        x, y, z = cloned.get_column_coordinates("sensor1")
        assert x == 1.0
        assert y == 2.0
        assert z == 3.0

        # 別のオブジェクトであることを確認
        cloned.set_column_coordinates("sensor1", x=10.0)
        orig_x, _, _ = original.get_column_coordinates("sensor1")
        clone_x, _, _ = cloned.get_column_coordinates("sensor1")
        assert orig_x == 1.0
        assert clone_x == 10.0

    def test_missing_column(self):
        """存在しない列へのアクセスエラーテスト"""
        coord_collection = CoordinateCollection(
            self.steps, {"sensor1": self.column1, "sensor2": self.column2}
        )

        # 存在しない列の座標を設定しようとする
        with pytest.raises(ValueError) as exc_info:
            coord_collection.set_column_coordinates("sensor3", x=1.0)

        assert "見つかりません" in str(exc_info.value)

        # 存在しない列の座標を取得しようとする
        with pytest.raises(ValueError) as exc_info:
            coord_collection.get_column_coordinates("sensor3")

        assert "見つかりません" in str(exc_info.value)

    def test_calculate_distance_error(self):
        """距離計算のエラー処理テスト"""
        coord_collection = CoordinateCollection(
            self.steps, {"sensor1": self.column1, "sensor2": self.column2}
        )

        # 座標が設定されていない状態で距離計算を試みる
        with pytest.raises(ValueError) as exc_info:
            coord_collection.calculate_distance("sensor1", "sensor2")

        assert "座標情報が不足" in str(exc_info.value)

        # 部分的な座標設定での距離計算
        coord_collection.set_column_coordinates("sensor1", x=1.0, y=1.0)
        coord_collection.set_column_coordinates("sensor2", x=2.0)  # y座標が欠けている

        with pytest.raises(ValueError) as exc_info:
            coord_collection.calculate_distance("sensor1", "sensor2")

        assert "座標情報が不足" in str(exc_info.value)

    def test_initialization_with_coordinates(self):
        """初期化時に座標情報を設定するテスト"""
        # 座標情報を辞書で定義
        coordinates = {
            "sensor1": {"x": 1.0, "y": 2.0, "z": 3.0},
            "sensor2": {"x": 4.0, "y": 5.0},  # zは指定せず
        }

        # 座標情報を指定して初期化
        coord_collection = CoordinateCollection(
            self.steps,
            {"sensor1": self.column1, "sensor2": self.column2},
            coordinates=coordinates,
        )

        # 座標が正しく設定されていることを確認
        x1, y1, z1 = coord_collection.get_column_coordinates("sensor1")
        assert x1 == 1.0
        assert y1 == 2.0
        assert z1 == 3.0

        x2, y2, z2 = coord_collection.get_column_coordinates("sensor2")
        assert x2 == 4.0
        assert y2 == 5.0
        assert z2 is None

        # 座標を持つカラムのリストが正しいことを確認
        columns_with_coords = coord_collection.get_columns_with_coordinates()
        assert set(columns_with_coords) == {"sensor1", "sensor2"}

    def test_initialization_with_custom_key_and_coordinates(self):
        """カスタムメタデータキーと座標情報を同時に指定するテスト"""
        # 座標情報を辞書で定義
        coordinates = {"sensor1": {"x": 10.0, "y": 20.0, "z": 30.0}}

        # カスタムメタデータキーと座標情報を指定して初期化
        coord_collection = CoordinateCollection(
            self.steps,
            {"sensor1": self.column1, "sensor2": self.column2},
            coordinate_metadata_key="position",
            coordinates=coordinates,
        )

        # カスタムキーが正しく設定されていることを確認
        assert coord_collection.coordinate_metadata_key == "position"

        # 座標が正しく設定されていることを確認
        x, y, z = coord_collection.get_column_coordinates("sensor1")
        assert x == 10.0
        assert y == 20.0
        assert z == 30.0

        # メタデータが正しいキーで保存されていることを確認
        assert "position" in coord_collection.columns["sensor1"].metadata
        assert coord_collection.columns["sensor1"].metadata["position"]["x"] == 10.0

    def test_factory_with_coordinates(self):
        """ファクトリ関数を使用して座標情報を設定するテスト"""
        from tascpy.domains.factory import DomainCollectionFactory

        # 座標情報を辞書で定義
        coordinates = {
            "sensor1": {"x": 5.0, "y": 6.0, "z": 7.0},
            "sensor2": {"x": 8.0, "y": 9.0, "z": 10.0},
        }

        # ファクトリ関数を使用して座標情報付きのコレクションを作成
        coord_collection = DomainCollectionFactory.create(
            "coordinate",
            step=self.steps,
            columns={"sensor1": self.column1, "sensor2": self.column2},
            coordinates=coordinates,
        )

        # インスタンスタイプの確認
        assert isinstance(coord_collection, CoordinateCollection)

        # 座標が正しく設定されていることを確認
        x1, y1, z1 = coord_collection.get_column_coordinates("sensor1")
        assert x1 == 5.0
        assert y1 == 6.0
        assert z1 == 7.0

        x2, y2, z2 = coord_collection.get_column_coordinates("sensor2")
        assert x2 == 8.0
        assert y2 == 9.0
        assert z2 == 10.0
