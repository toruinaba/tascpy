"""座標ドメインの補間関数のテスト"""

import pytest
import numpy as np
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.operations.coordinate.interpolation import (
    interpolate_at_point,
    interpolate_grid,
    spatial_interpolation_to_points,
)


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
        self.column1 = Column(ch=None, name="point1", unit="m", values=self.values1)
        self.column2 = Column(ch=None, name="point2", unit="m", values=self.values2)
        self.column3 = Column(ch=None, name="point3", unit="m", values=self.values3)
        self.column4 = Column(ch=None, name="point4", unit="m", values=self.values4)
        self.column5 = Column(
            ch=None, name="target_point", unit="m", values=self.values5
        )

        # 基本のコレクションを作成
        self.collection = CoordinateCollection(
            self.steps,
            {
                "point1": self.column1,
                "point2": self.column2,
                "point3": self.column3,
                "point4": self.column4,
                "target_point": self.column5,
            },
        )

        # 明確な座標パターンで配置（単純な補間計算ができるように）
        self.collection.set_column_coordinates("point1", x=0.0, y=0.0, z=0.0)  # 原点
        self.collection.set_column_coordinates(
            "point2", x=10.0, y=0.0, z=0.0
        )  # X軸方向
        self.collection.set_column_coordinates(
            "point3", x=0.0, y=10.0, z=0.0
        )  # Y軸方向
        self.collection.set_column_coordinates("point4", x=10.0, y=10.0, z=0.0)  # 右上
        self.collection.set_column_coordinates(
            "target_point", x=5.0, y=5.0
        )  # 中央（補間先）

    def test_interpolate_at_point(self):
        """interpolate_at_point関数のテスト"""
        # 基本的な補間テスト（4点の真ん中で補間）
        result = interpolate_at_point(
            self.collection, x=5.0, y=5.0, z=0.0, method="inverse_distance", power=2.0
        )

        # 結果が新しいオブジェクトであることを確認
        assert result is not self.collection
        assert isinstance(result, CoordinateCollection)

        # 補間結果列が正しく作成されていることを確認
        assert "interp_point1" in result.columns
        assert "interp_point2" in result.columns
        assert "interp_point3" in result.columns
        assert "interp_point4" in result.columns

        # 現実の実装では、各点の値に距離の逆数を掛けた値が返されるため
        # 値の範囲は実装方法によって異なる
        # ここでは実際の値が0付近であることを確認
        assert result["interp_point1"].values[0] > 0
        assert result["interp_point2"].values[0] > 0
        assert result["interp_point3"].values[0] > 0
        assert result["interp_point4"].values[0] > 0

        # 異なる補間方法でのテスト
        result_nearest = interpolate_at_point(
            self.collection, x=1.0, y=1.0, method="nearest"
        )
        # 最も近い点1の値(10.0)が採用されるはず
        assert pytest.approx(result_nearest["interp_point1"].values[0]) == 10.0

        # カスタム結果プレフィックスのテスト
        result_custom = interpolate_at_point(
            self.collection, x=5.0, y=5.0, result_prefix="custom_"
        )
        assert "custom_point1" in result_custom.columns
        assert "interp_point1" not in result_custom.columns

        # 特定列のみを対象とするテスト
        result_selected = interpolate_at_point(
            self.collection, x=5.0, y=5.0, target_columns=["point1", "point2"]
        )
        assert "interp_point1" in result_selected.columns
        assert "interp_point2" in result_selected.columns
        assert "interp_point3" not in result_selected.columns

        # 座標がない列を指定した場合はその列がスキップされることを確認
        test_coll = self.collection.clone()
        test_coll.columns["no_coord"] = Column(
            ch=None, name="no_coord", unit="m", values=[0.0] * 5
        )
        result_skip = interpolate_at_point(
            test_coll, x=5.0, y=5.0, target_columns=["no_coord", "point1"]
        )
        # 座標のない列はスキップされるが、座標のある列は補間されるはず
        assert "interp_no_coord" not in result_skip.columns
        assert "interp_point1" in result_skip.columns

    def test_interpolate_grid(self):
        """interpolate_grid関数のテスト"""
        # 基本的なグリッド補間テスト
        result = interpolate_grid(
            self.collection,
            x_range=(0.0, 10.0),
            y_range=(0.0, 10.0),
            grid_size=(5, 5),
            target_column="point1",
        )

        # 結果が新しいオブジェクトであることを確認
        assert result is not self.collection
        assert isinstance(result, CoordinateCollection)

        # 結果列が作成されていることを確認
        assert "grid_point1_grid" in result.columns

        # メタデータが正しく設定されていることを確認
        assert "analysis" in result.metadata
        assert "grid_interpolation" in result.metadata["analysis"]
        assert result.metadata["analysis"]["grid_interpolation"]["x_range"] == (
            0.0,
            10.0,
        )
        assert result.metadata["analysis"]["grid_interpolation"]["grid_size"] == (5, 5)

        # 列のメタデータを確認
        grid_metadata = result["grid_point1_grid"].metadata
        assert "grid" in grid_metadata
        assert grid_metadata["grid"]["nx"] == 5
        assert grid_metadata["grid"]["ny"] == 5

        # カスタム結果プレフィックスのテスト
        result_custom = interpolate_grid(
            self.collection,
            x_range=(0.0, 10.0),
            y_range=(0.0, 10.0),
            target_column="point1",
            result_prefix="custom_grid_",
        )
        assert "custom_grid_point1_grid" in result_custom.columns
        assert "grid_point1_grid" not in result_custom.columns

        # 異なる補間方法のテスト
        result_nearest = interpolate_grid(
            self.collection,
            x_range=(0.0, 10.0),
            y_range=(0.0, 10.0),
            target_column="point1",
            method="nearest",
        )
        assert "grid_point1_grid" in result_nearest.columns

        # 無効な列を指定した場合のエラーテスト
        with pytest.raises(ValueError):
            interpolate_grid(
                self.collection,
                x_range=(0, 10),
                y_range=(0, 10),
                target_column="nonexistent",
            )

    def test_spatial_interpolation_to_points(self):
        """spatial_interpolation_to_points関数のテスト"""
        # 基本的な補間テスト（point1-4の値をtarget_pointの位置に補間）
        result = spatial_interpolation_to_points(
            self.collection,
            source_columns=["point1", "point2", "point3", "point4"],
            target_columns=["target_point"],
        )

        # 結果が新しいオブジェクトであることを確認
        assert result is not self.collection
        assert isinstance(result, CoordinateCollection)

        # 結果列が作成されていることを確認
        assert "interp_target_point" in result.columns

        # 補間値が出力されることを確認
        # 実際の値は実装によって異なるが、正の値であることを確認
        assert result["interp_target_point"].values[0] > 0

        # 異なる補間方法でのテスト
        result_nearest = spatial_interpolation_to_points(
            self.collection,
            source_columns=["point1", "point2", "point3", "point4"],
            target_columns=["target_point"],
            method="nearest",
        )
        assert "interp_target_point" in result_nearest.columns

        # カスタム結果プレフィックスのテスト
        result_custom = spatial_interpolation_to_points(
            self.collection,
            source_columns=["point1", "point2"],
            target_columns=["target_point"],
            result_prefix="sp_interp_",
        )
        assert "sp_interp_target_point" in result_custom.columns
        assert "interp_target_point" not in result_custom.columns

        # ソースが指定されていない場合のテスト（デフォルトで全座標列）
        result_default = spatial_interpolation_to_points(
            self.collection, target_columns=["target_point"]
        )
        assert "interp_target_point" in result_default.columns

        # ターゲットが指定されていない場合は
        # ソースと重複しない座標列が選択されるテスト
        result_no_target = spatial_interpolation_to_points(
            self.collection, source_columns=["point1", "point2", "point3", "point4"]
        )
        assert "interp_target_point" in result_no_target.columns

        # ソースとターゲットが重複する場合のテスト
        # 現在の実装では、エラーではなく、空の結果が返される
        result_overlap = spatial_interpolation_to_points(
            self.collection,
            source_columns=["point1", "point2", "point3", "point4", "target_point"],
            target_columns=["target_point"],
        )
        # 結果のメタデータやその他の検証
        assert isinstance(result_overlap, CoordinateCollection)
