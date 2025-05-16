"""座標ドメインの基本操作関数のテスト"""

import pytest
import numpy as np
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.operations.coordinate.basic import (
    get_column_coordinates,
    set_column_coordinates,
    get_columns_with_coordinates,
)


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
        """get_column_coordinates関数のテスト"""
        # 完全な座標を持つセンサー
        coords = get_column_coordinates(self.collection, "sensor1")
        assert coords["x"] == 1.0
        assert coords["y"] == 2.0
        assert coords["z"] == 3.0

        # 部分的な座標を持つセンサー
        coords = get_column_coordinates(self.collection, "sensor2")
        assert coords["x"] == 4.0
        assert coords["y"] == 5.0
        assert coords["z"] is None

        # 座標が未設定のセンサー
        coords = get_column_coordinates(self.collection, "sensor3")
        assert coords["x"] is None
        assert coords["y"] is None
        assert coords["z"] is None

    def test_set_column_coordinates(self):
        """set_column_coordinates関数のテスト"""
        # 座標を新規設定
        result = set_column_coordinates(self.collection, "sensor3", x=7.0, y=8.0, z=9.0)

        # 結果が新しいオブジェクトであることを確認
        assert result is not self.collection
        assert isinstance(result, CoordinateCollection)

        # 座標が正しく設定されていることを確認
        coords = get_column_coordinates(result, "sensor3")
        assert coords["x"] == 7.0
        assert coords["y"] == 8.0
        assert coords["z"] == 9.0

        # 元のオブジェクトは変更されていないことを確認
        coords = get_column_coordinates(self.collection, "sensor3")
        assert coords["x"] is None
        assert coords["y"] is None
        assert coords["z"] is None

        # 座標の一部を更新
        updated = set_column_coordinates(result, "sensor1", y=20.0)
        coords = get_column_coordinates(updated, "sensor1")
        assert coords["x"] == 1.0  # 変更なし
        assert coords["y"] == 20.0  # 更新された
        assert coords["z"] == 3.0  # 変更なし

    def test_get_columns_with_coordinates(self):
        """get_columns_with_coordinates関数のテスト"""
        # 初期状態では2つの列に座標がある
        columns = get_columns_with_coordinates(self.collection)
        assert len(columns) == 2
        assert "sensor1" in columns
        assert "sensor2" in columns
        assert "sensor3" not in columns

        # 3つ目の列に座標を設定
        updated = set_column_coordinates(self.collection, "sensor3", x=1.0)
        columns = get_columns_with_coordinates(updated)
        assert len(columns) == 3
        assert "sensor3" in columns
