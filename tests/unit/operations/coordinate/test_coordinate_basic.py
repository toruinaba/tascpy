"""座標ドメインの基本操作関数およびコレクションメソッドのテスト"""

import pytest
import numpy as np
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.analytics.operations.coordinate.basic import extract_coordinates


class TestCoordinateBasic:
    """座標ドメインの基本操作関数のテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # テスト用のデータを作成
        self.steps = list(range(5))
        self.values1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.values2 = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.values3 = [100.0, 200.0, 300.0, 400.0, 500.0]

        # Columnオブジェクトを作成
        self.column1 = Column(ch=None, name="sensor1", unit="m", values=self.values1)
        self.column2 = Column(ch=None, name="sensor2", unit="m", values=self.values2)
        self.column3 = Column(ch=None, name="sensor3", unit="m", values=self.values3)

        # 基本のコレクションを作成
        self.collection = CoordinateCollection(
            self.steps,
            {"sensor1": self.column1, "sensor2": self.column2, "sensor3": self.column3},
        )

        # いくつかの座標を設定
        self.collection.set_column_coordinates("sensor1", x=1.0, y=2.0, z=3.0)
        self.collection.set_column_coordinates("sensor2", x=4.0, y=5.0)  # zは未設定

    def test_get_column_coordinates(self):
        """get_column_coordinatesメソッドのテスト"""
        # 完全な座標を持つセンサー
        x, y, z = self.collection.get_column_coordinates("sensor1")
        assert x == 1.0
        assert y == 2.0
        assert z == 3.0

        # 部分的な座標を持つセンサー
        x, y, z = self.collection.get_column_coordinates("sensor2")
        assert x == 4.0
        assert y == 5.0
        assert z is None

        # 座標が未設定のセンサー
        x, y, z = self.collection.get_column_coordinates("sensor3")
        assert x is None
        assert y is None
        assert z is None

    def test_set_column_coordinates(self):
        """set_column_coordinatesメソッドのテスト"""
        # 座標を新規設定
        self.collection.set_column_coordinates("sensor3", x=7.0, y=8.0, z=9.0)

        # 座標が正しく設定されていることを確認
        x, y, z = self.collection.get_column_coordinates("sensor3")
        assert x == 7.0
        assert y == 8.0
        assert z == 9.0

        # 座標の一部を更新
        self.collection.set_column_coordinates("sensor1", y=20.0)
        x, y, z = self.collection.get_column_coordinates("sensor1")
        assert x == 1.0  # 変更なし
        assert y == 20.0  # 更新された
        assert z == 3.0  # 変更なし

    def test_get_columns_with_coordinates(self):
        """get_columns_with_coordinatesメソッドのテスト"""
        # 初期状態では2つの列に座標がある
        columns = self.collection.get_columns_with_coordinates()
        assert len(columns) == 2
        assert "sensor1" in columns
        assert "sensor2" in columns
        assert "sensor3" not in columns

        # 3つ目の列に座標を設定
        self.collection.set_column_coordinates("sensor3", x=1.0)
        columns = self.collection.get_columns_with_coordinates()
        assert len(columns) == 3
        assert "sensor3" in columns

    def test_extract_coordinates(self):
        """extract_coordinates関数のテスト"""
        # 座標を抽出
        result = extract_coordinates(self.collection)

        # 結果のコレクションには元の列と新しい座標列が含まれるべき
        assert "sensor1" in result.columns
        assert "coord_sensor1_x" in result.columns
        assert "coord_sensor1_y" in result.columns
        assert "coord_sensor1_z" in result.columns

        assert "sensor2" in result.columns
        assert "coord_sensor2_x" in result.columns
        assert "coord_sensor2_y" in result.columns
        assert "coord_sensor2_z" not in result.columns  # zは未設定だったため含まれない

        # 座標が抽出されていない列（元のまま）
        assert "sensor3" in result.columns
        assert "coord_sensor3_x" not in result.columns

        # 新しい列の値を確認
        np.testing.assert_array_equal(
            result.columns["coord_sensor1_x"].values,
            np.array([1.0, 1.0, 1.0, 1.0, 1.0]),
        )
        np.testing.assert_array_equal(
            result.columns["coord_sensor1_y"].values,
            np.array([2.0, 2.0, 2.0, 2.0, 2.0]),
        )
        np.testing.assert_array_equal(
            result.columns["coord_sensor1_z"].values,
            np.array([3.0, 3.0, 3.0, 3.0, 3.0]),
        )

        np.testing.assert_array_equal(
            result.columns["coord_sensor2_x"].values,
            np.array([4.0, 4.0, 4.0, 4.0, 4.0]),
        )
        np.testing.assert_array_equal(
            result.columns["coord_sensor2_y"].values,
            np.array([5.0, 5.0, 5.0, 5.0, 5.0]),
        )

        # カスタム接頭辞のテスト
        result2 = extract_coordinates(self.collection, result_prefix="my_prefix_")
        assert "my_prefix_sensor1_x" in result2.columns
