"""荷重-変位ドメインの曲線生成関数のテスト"""

import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.load_displacement import LoadDisplacementCollection


class TestLoadDisplacementCurves:
    """荷重-変位ドメインの曲線生成関数のテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # 単一サイクルの荷重-変位データ
        self.steps = list(range(5))
        self.loads = [0, 10, 20, 10, 0]
        self.displacements = [0, 1, 2, 3, 4]
        self.cycles = [1, 1, 1, 1, 1]

        # 基本のコレクションを作成
        collection = ColumnCollection({"load": self.loads, "displacement": self.displacements, "cycle": self.cycles}, step=self.steps)

        # 荷重-変位コレクションを作成
        self.ld_collection = collection.ops.as_load_displacement("load", "displacement").end()

        # 複数サイクルの荷重-変位データ
        multi_steps = list(range(15))
        multi_loads = [0, 10, 20, 10, 0, -10, -20, -10, 0, 15, 30, 15, 0, -15, -30]
        multi_displacements = [0, 1, 2, 1, 0, -1, -2, -1, 0, 1.5, 3, 1.5, 0, -1.5, -3]

        # サイクルマーカーを作成
        cycles = [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4]

        multi_collection = ColumnCollection({"load": multi_loads, "displacement": multi_displacements, "cycle": cycles}, step=multi_steps)

        # 複数サイクルの荷重-変位コレクション
        self.multi_cycle_collection = multi_collection.ops.as_load_displacement("load", "displacement").end()

    def test_create_skeleton_curve_basic(self):
        """create_skeleton_curve関数の基本機能テスト"""
        # スケルトン曲線を作成。引数を明示的に指定
        result = self.ld_collection.ops.create_skeleton_curve(
            cycle_column="cycle"
        ).end()

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果は results 辞書に格納される
        assert "skeleton_curve" in result.results

        curve = result.results["skeleton_curve"]
        curve_data = curve.to_dict()["data"]

        # 最大荷重が含まれることを確認
        assert max(self.loads) in curve_data["y"]

        # 最大値のインデックスを取得
        max_idx = self.loads.index(max(self.loads))
        assert self.displacements[max_idx] in curve_data["x"]

    def test_create_skeleton_curve_with_decrease(self):
        """減少部分を含むスケルトン曲線のテスト"""
        # 複数サイクルの場合
        result = self.multi_cycle_collection.ops.create_skeleton_curve(
            cycle_column="cycle",
            has_decrease=True,
            decrease_type="envelope"
        ).end()

        curve_data = result.results["skeleton_curve"].to_dict()["data"]
        p_ske = curve_data["y"]
        d_ske = curve_data["x"]

        # 正側の最大応答値を確認
        assert max(self.multi_cycle_collection["load"].values) in p_ske

        # 減少側も含まれていることを確認（長さが2以上）
        assert len(p_ske) > 2
        assert len(d_ske) > 2

    def test_create_skeleton_curve_decrease_types(self):
        """異なる減少部分の処理方法のテスト"""
        
        envelope_result = self.multi_cycle_collection.ops.create_skeleton_curve(cycle_column="cycle", has_decrease=True, decrease_type="envelope").end()
        continuous_result = self.multi_cycle_collection.ops.create_skeleton_curve(cycle_column="cycle", has_decrease=True, decrease_type="continuous_only").end()
        both_result = self.multi_cycle_collection.ops.create_skeleton_curve(cycle_column="cycle", has_decrease=True, decrease_type="both").end()

        # それぞれ結果が異なることを確認
        env_len = len(envelope_result.results["skeleton_curve"].to_dict()["data"]["y"])
        cont_len = len(continuous_result.results["skeleton_curve"].to_dict()["data"]["y"])
        both_len = len(both_result.results["skeleton_curve"].to_dict()["data"]["y"])

        # 少なくとも一つは異なる長さになるはず
        assert env_len != cont_len or env_len != both_len or cont_len != both_len

    def test_create_cumulative_curve_basic(self):
        """create_cumulative_curve関数の基本機能テスト"""
        # 累積曲線を作成
        result = self.multi_cycle_collection.ops.create_cumulative_curve(
            cycle_column="cycle"
        ).end()

        assert "cumulative_curve" in result.results

        # 累積曲線の値を取得
        curve_data = result.results["cumulative_curve"].to_dict()["data"]
        p_cum = curve_data["y"]
        d_cum = curve_data["x"]

        # 非空の結果であることを確認
        assert len(p_cum) > 0
        assert len(d_cum) > 0

        # 元の正の荷重が含まれていることを確認
        pos_loads = [l for l in self.multi_cycle_collection["load"].values if l > 0]
        for load in pos_loads:
            # 少なくとも一つの荷重値が累積曲線に含まれていることを確認
            if load in p_cum:
                assert True
                break
        else:
            assert False, "元の正の荷重値が累積曲線に含まれていません"
