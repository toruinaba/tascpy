"""座標ドメインの距離計算関数のテスト"""

import pytest
import numpy as np
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.operations.coordinate.distance import (
    calculate_distance,
    find_nearest_neighbors,
    spatial_clustering,
)


class TestCoordinateDistance:
    """座標ドメインの距離計算関数のテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # テスト用のデータを作成
        self.steps = list(range(5))
        self.values1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.values2 = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.values3 = [100.0, 200.0, 300.0, 400.0, 500.0]
        self.values4 = [1000.0, 2000.0, 3000.0, 4000.0, 5000.0]

        # Columnオブジェクトを作成
        self.column1 = Column(ch=None, name="sensor1", unit="m", values=self.values1)
        self.column2 = Column(ch=None, name="sensor2", unit="m", values=self.values2)
        self.column3 = Column(ch=None, name="sensor3", unit="m", values=self.values3)
        self.column4 = Column(ch=None, name="sensor4", unit="m", values=self.values4)

        # 基本のコレクションを作成
        self.collection = CoordinateCollection(
            self.steps,
            {
                "sensor1": self.column1,
                "sensor2": self.column2,
                "sensor3": self.column3,
                "sensor4": self.column4,
            },
        )

        # センサーに座標を設定
        self.collection.set_column_coordinates("sensor1", x=0.0, y=0.0, z=0.0)
        self.collection.set_column_coordinates(
            "sensor2", x=3.0, y=4.0, z=0.0
        )  # 原点から5m
        self.collection.set_column_coordinates(
            "sensor3", x=10.0, y=0.0, z=0.0
        )  # X軸上に10m
        self.collection.set_column_coordinates(
            "sensor4", x=0.0, y=0.0, z=0.0
        )  # Z座標も設定

    def test_calculate_distance(self):
        """calculate_distance関数のテスト"""
        # 3D座標を持つセンサー間の距離
        dist = calculate_distance(self.collection, "sensor1", "sensor2")
        assert pytest.approx(dist) == 5.0  # 3-4-5の直角三角形

        # X軸に沿った距離
        dist = calculate_distance(self.collection, "sensor1", "sensor3")
        assert pytest.approx(dist) == 10.0

        # Z座標がないセンサーを含む距離計算
        dist = calculate_distance(self.collection, "sensor1", "sensor4")
        assert pytest.approx(dist) == 0.0  # 同じXY座標

        # 存在しない列を指定した場合

    with pytest.raises(ValueError):
        calculate_distance(self.collection, "sensor1", "nonexistent")

    def test_find_nearest_neighbors(self):
        """find_nearest_neighbors関数のテスト"""
        # デフォルト（3つの近傍）
        result = find_nearest_neighbors(self.collection, "sensor1")

        # 結果が新しいオブジェクトであることを確認
        assert result is not self.collection
        assert isinstance(result, CoordinateCollection)

        # メタデータに近傍情報が保存されていることを確認
        assert "analysis" in result.metadata
        assert "nearest_neighbors" in result.metadata["analysis"]
        assert "reference_column" in result.metadata["analysis"]["nearest_neighbors"]
        assert "neighbors" in result.metadata["analysis"]["nearest_neighbors"]

        # 結果列が作成されていることを確認
        assert "neighbors_of_sensor1" in result.columns

        # 近傍のセンサーが正しいことを確認
        neighbors = result.metadata["analysis"]["nearest_neighbors"]["neighbors"]
        assert len(neighbors) == 3
        # 距離順に並んでいることを確認
        assert neighbors[0]["column"] == "sensor4"  # 0mで最も近い
        assert neighbors[1]["column"] == "sensor2"  # 5m
        assert neighbors[2]["column"] == "sensor3"  # 10m

        # 近傍数を指定した場合
        result_n2 = find_nearest_neighbors(self.collection, "sensor1", n_neighbors=2)
        neighbors_n2 = result_n2.metadata["analysis"]["nearest_neighbors"]["neighbors"]
        assert len(neighbors_n2) == 2
        assert neighbors_n2[0]["column"] == "sensor4"
        assert neighbors_n2[1]["column"] == "sensor2"

        # カスタム結果列名を指定した場合
        result_custom = find_nearest_neighbors(
            self.collection, "sensor1", result_column="nearest_to_sensor1"
        )
        assert "nearest_to_sensor1" in result_custom.columns
        assert "neighbors_of_sensor1" not in result_custom.columns

        # 座標がない列を指定した場合のエラー
        test_coll = self.collection.clone()
        test_coll.columns["no_coord"] = Column(
            ch=None, name="no_coord", unit="m", values=[0.0] * 5
        )
        with pytest.raises(ValueError):
            find_nearest_neighbors(test_coll, "no_coord")

    def test_spatial_clustering(self):
        """spatial_clustering関数のテスト"""
        # シンプルなケースのクラスタリング（2クラスタ）
        result = spatial_clustering(self.collection, n_clusters=2)

        # 結果が新しいオブジェクトであることを確認
        assert result is not self.collection
        assert isinstance(result, CoordinateCollection)

        # メタデータにクラスタリング結果が保存されていることを確認
        assert "analysis" in result.metadata
        assert "clustering" in result.metadata["analysis"]
        assert "algorithm" in result.metadata["analysis"]["clustering"]
        assert "n_clusters" in result.metadata["analysis"]["clustering"]
        assert "clusters" in result.metadata["analysis"]["clustering"]

        # クラスタ数が正しいことを確認
        clusters = result.metadata["analysis"]["clustering"]["clusters"]
        assert len(clusters) == 2

        # 結果列が作成されていることを確認
        assert "cluster" in result.columns

        # カスタム結果列名を指定した場合
        result_custom = spatial_clustering(
            self.collection, n_clusters=2, result_column="groups"
        )
        assert "groups" in result_custom.columns
        assert "cluster" not in result_custom.columns

        # 異なるアルゴリズムを指定した場合
        result_hierarch = spatial_clustering(self.collection, algorithm="hierarchical")
        assert (
            result_hierarch.metadata["analysis"]["clustering"]["algorithm"]
            == "hierarchical"
        )

        # クラスタ数が列数より多い場合のエラー
        with pytest.raises(ValueError):
            spatial_clustering(self.collection, n_clusters=5)
