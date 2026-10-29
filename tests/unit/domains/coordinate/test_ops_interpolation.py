"""座標ドメインの補間関数のテスト"""

import pytest
import numpy as np
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection


class TestCoordinateInterpolation:
    """座標ドメインの補間関数のテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # テスト用のデータを作成
        self.steps = list(range(5))

        # 複数のデータポイント（異なる座標に配置）を用意
        self.values1 = [10.0, 10.0, 10.0, 10.0, 10.0]  # 点(0,0,0)に値10
        self.values2 = [20.0, 20.0, 20.0, 20.0, 20.0]  # 点(10,0,0)に値20
        self.values3 = [30.0, 30.0, 30.0, 30.0, 30.0]  # 点(0,10,0)に値30
        self.values4 = [40.0, 40.0, 40.0, 40.0, 40.0]  # 点(10,10,0)に値40
        self.values5 = [50.0, 50.0, 50.0, 50.0, 50.0]  # 補間先用のポイント

        # Columnオブジェクトを作成
        self.column1 = Column("point1", unit="m", values=self.values1)
        self.column2 = Column("point2", unit="m", values=self.values2)
        self.column3 = Column("point3", unit="m", values=self.values3)
        self.column4 = Column("point4", unit="m", values=self.values4)
        self.column5 = Column("target_point", unit="m", values=self.values5
        )

        # 基本のコレクションを作成
        self.collection = CoordinateCollection({
                "point1": self.column1,
                "point2": self.column2,
                "point3": self.column3,
                "point4": self.column4,
                "target_point": self.column5,
            }, step=self.steps)

        # 明確な座標パターンで配置（単純な補間計算ができるように）
        self.collection = (
            self.collection.with_coordinates("point1", x=0.0, y=0.0, z=0.0)  # 原点
            .with_coordinates("point2", x=10.0, y=0.0, z=0.0)  # X軸方向
            .with_coordinates("point3", x=0.0, y=10.0, z=0.0)  # Y軸方向
            .with_coordinates("point4", x=10.0, y=10.0, z=0.0)  # 右上
            .with_coordinates("target_point", x=5.0, y=5.0)  # 中央（補間先）
        )

    CORNERS = ["point1", "point2", "point3", "point4"]

    def test_interpolate_at_point(self):
        """4 隅から等距離の中心では 4 点の平均になる（z を指定すると z を持つ列だけが補間元）"""
        result = self.collection.ops.interpolate_at_point(x=5.0, y=5.0, z=0.0).end()

        assert result is not self.collection
        assert isinstance(result, CoordinateCollection)
        assert result.columns[-1] == "interp(5, 5, 0)"
        col = result["interp(5, 5, 0)"]
        np.testing.assert_allclose(col.values, [25.0] * 5)
        assert col.unit == "m"
        assert result.get_column_coordinates("interp(5, 5, 0)") == (5.0, 5.0, 0.0)
        assert col.attrs["interpolation"]["source_columns"] == self.CORNERS

    def test_interpolate_at_point_uses_coincident_source(self):
        """補間点に補間元の点があればその値（target_point は (5, 5) に値 50）"""
        result = self.collection.ops.interpolate_at_point(x=5.0, y=5.0, result_column="c").end()
        np.testing.assert_allclose(result["c"].values, [50.0] * 5)

    def test_interpolate_at_point_inverse_distance_value(self):
        result = self.collection.ops.interpolate_at_point(
            x=2.5, y=0.0, source_columns=["point1", "point2"], result_column="v",
        ).end()
        w1, w2 = 1 / 2.5**2, 1 / 7.5**2
        np.testing.assert_allclose(result["v"].values, (10 * w1 + 20 * w2) / (w1 + w2))

    def test_interpolate_at_point_nearest(self):
        result = self.collection.ops.interpolate_at_point(x=1.0, y=1.0, method="nearest", result_column="n").end()
        np.testing.assert_allclose(result["n"].values, [10.0] * 5)

    def test_interpolate_at_point_per_row_and_missing(self):
        """行ごとに補間し、欠損の補間元はその行だけ除く"""
        coll = self.collection.with_column("point1", [10.0, None, 10.0, 10.0, 10.0])
        result = coll.ops.interpolate_at_point(
            x=5.0, y=0.0, source_columns=["point1", "point2"], result_column="v",
        ).end()
        np.testing.assert_allclose(result["v"].values, [15.0, 20.0, 15.0, 15.0, 15.0])

    def test_interpolate_at_point_skips_columns_without_coordinates(self):
        coll = self.collection.with_column("no_coord", [0.0] * 5, unit="m")
        result = coll.ops.interpolate_at_point(
            x=0.0, y=0.0, source_columns=["no_coord", "point1"], result_column="v",
        ).end()
        np.testing.assert_allclose(result["v"].values, [10.0] * 5)

    def test_interpolate_at_point_mixed_units_is_none(self):
        coll = self.collection.with_meta("point2", unit="mm")
        result = coll.ops.interpolate_at_point(x=1.0, y=0.0, source_columns=["point1", "point2"]).end()
        assert result[result.columns[-1]].unit is None

    def test_invalid_method(self):
        with pytest.raises(ValueError, match="inverse_distance"):
            self.collection.ops.interpolate_at_point(x=0.0, y=0.0, method="linear")

    def test_grid(self):
        """グリッドの値を GridResult として返す"""
        grid = self.collection.ops.grid(
            x_range=(0.0, 10.0), y_range=(0.0, 10.0), grid_size=(3, 3), source_columns=self.CORNERS)

        np.testing.assert_allclose(grid.x, [0.0, 5.0, 10.0])
        np.testing.assert_allclose(grid.y, [0.0, 5.0, 10.0])
        assert grid.values.shape == (3, 3)
        # 隅は補間元の値、中心は 4 点の平均
        assert grid.values[0, 0] == 10.0
        assert grid.values[0, 2] == 20.0
        assert grid.values[2, 0] == 30.0
        assert grid.values[2, 2] == 40.0
        assert np.isclose(grid.values[1, 1], 25.0)
        assert grid.unit == "m"
        assert grid.metadata["row"] == 0

    def test_grid_row(self):
        coll = self.collection.with_column("point1", [10.0, 10.0, 10.0, 10.0, 100.0])
        grid = coll.ops.grid(
            x_range=(0.0, 0.0), y_range=(0.0, 0.0), grid_size=(1, 1), source_columns=self.CORNERS,
            row=-1, method="nearest")
        assert grid.values[0, 0] == 100.0
        assert grid.metadata["step"] == 4
        with pytest.raises(IndexError):
            coll.ops.grid(x_range=(0, 1), y_range=(0, 1), row=5)

    def test_spatial_interpolation_to_points(self):
        """補間先の列の座標位置で、補間元の列から行ごとに補間する"""
        result = self.collection.ops.spatial_interpolation_to_points(
            source_columns=self.CORNERS, target_columns=["target_point"],
        ).end()

        assert isinstance(result, CoordinateCollection)
        np.testing.assert_allclose(result["interp_target_point"].values, [25.0] * 5)
        assert result["interp_target_point"].unit == "m"
        assert result.get_column_coordinates("interp_target_point") == (5.0, 5.0, None)

        nearest = self.collection.ops.spatial_interpolation_to_points(
            source_columns=["point1", "point2"], target_columns=["target_point"], method="nearest",
            result_prefix="sp_",
        ).end()
        assert "sp_target_point" in nearest.columns

    def test_spatial_interpolation_default_targets(self):
        """補間先を省略すると、補間元以外の座標を持つ列が補間先になる"""
        result = self.collection.ops.spatial_interpolation_to_points(source_columns=self.CORNERS).end()
        assert result.columns[-1] == "interp_target_point"
        with pytest.raises(ValueError, match="補間先"):
            self.collection.ops.spatial_interpolation_to_points()

    def test_requires_coordinates(self):
        """座標を持つ列がない場合は ValueError"""
        no_coords = CoordinateCollection({"a": Column("a", unit="m", values=[1.0, 2.0])}, step=[0, 1])
        with pytest.raises(ValueError, match="有効な座標データがありません"):
            no_coords.ops.interpolate_at_point(x=0.0, y=0.0)
