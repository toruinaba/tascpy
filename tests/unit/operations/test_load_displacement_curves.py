"""荷重-変位ドメインの曲線生成関数のテスト"""

import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.operations.load_displacement.curves import (
    create_skeleton_curve,
    create_cumulative_curve,
)
from tascpy.operations.load_displacement.cycles import cycle_count


class TestLoadDisplacementCurves:
    """荷重-変位ドメインの曲線生成関数のテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # 単一サイクルの荷重-変位データ
        self.steps = list(range(5))
        self.loads = [0, 10, 20, 10, 0]
        self.displacements = [0, 1, 2, 3, 4]

        # 基本のコレクションを作成
        collection = ColumnCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # 荷重-変位コレクションを作成
        self.ld_collection = LoadDisplacementCollection(
            step=collection.step,
            columns=collection.columns,
            load_column="load",
            displacement_column="displacement",
        )

        # 複数サイクルの荷重-変位データ
        multi_steps = list(range(15))
        multi_loads = [0, 10, 20, 10, 0, -10, -20, -10, 0, 15, 30, 15, 0, -15, -30]
        multi_displacements = [0, 1, 2, 1, 0, -1, -2, -1, 0, 1.5, 3, 1.5, 0, -1.5, -3]

        # サイクルマーカーを作成
        cycles = [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4]

        multi_collection = ColumnCollection(
            multi_steps,
            {"load": multi_loads, "displacement": multi_displacements, "cycle": cycles},
        )

        # 複数サイクルの荷重-変位コレクション
        self.multi_cycle_collection = LoadDisplacementCollection(
            step=multi_collection.step,
            columns=multi_collection.columns,
            load_column="load",
            displacement_column="displacement",
        )

        # カスタムカラム名の荷重-変位コレクションも作成
        custom_collection = ColumnCollection(
            self.steps, {"force": self.loads, "disp": self.displacements}
        )

        self.custom_ld_collection = LoadDisplacementCollection(
            step=custom_collection.step,
            columns=custom_collection.columns,
            load_column="force",
            displacement_column="disp",
        )

    def test_create_skeleton_curve_basic(self):
        """create_skeleton_curve関数の基本機能テスト"""
        # スケルトン曲線を作成
        result = create_skeleton_curve(self.ld_collection)

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列の存在を確認
        assert "load_skeleton" in result.columns
        assert "displacement_skeleton" in result.columns

        # スケルトン曲線の値を確認
        p_ske = result["load_skeleton"].values
        d_ske = result["displacement_skeleton"].values

        # 最大荷重が含まれることを確認
        assert max(self.loads) in p_ske

        # 最大値のインデックスを取得
        max_idx = self.loads.index(max(self.loads))

        # 最大値の対応する変位が含まれていることを確認
        assert self.displacements[max_idx] in d_ske

    def test_create_skeleton_curve_custom_names(self):
        """カスタムカラム名での create_skeleton_curve 関数のテスト"""
        # カスタム出力カラム名を指定してスケルトン曲線を作成
        result = create_skeleton_curve(
            self.custom_ld_collection,
            result_load_column="force_skl",
            result_disp_column="disp_skl",
        )

        # カスタム結果列の存在を確認
        assert "force_skl" in result.columns
        assert "disp_skl" in result.columns

        # もとのカラム名に基づく自動生成名がないことを確認
        assert "force_skeleton" not in result.columns
        assert "disp_skeleton" not in result.columns

    def test_create_skeleton_curve_with_decrease(self):
        """減少部分を含むスケルトン曲線のテスト"""
        # 複数サイクルの場合
        result = create_skeleton_curve(
            self.multi_cycle_collection, has_decrease=True, decrease_type="envelope"
        )

        # 結果列の存在を確認
        assert "load_skeleton" in result.columns
        assert "displacement_skeleton" in result.columns

        # スケルトン曲線の値を取得
        p_ske = result["load_skeleton"].values
        d_ske = result["displacement_skeleton"].values

        # 正側の最大応答値を確認
        assert max(self.multi_cycle_collection["load"].values) in p_ske

        # 減少側も含まれていることを確認（長さが2以上）
        assert len(p_ske) > 2
        assert len(d_ske) > 2

    def test_create_skeleton_curve_decrease_types(self):
        """異なる減少部分の処理方法のテスト"""
        # envelope
        envelope_result = create_skeleton_curve(
            self.multi_cycle_collection, has_decrease=True, decrease_type="envelope"
        )

        # continuous_only
        continuous_result = create_skeleton_curve(
            self.multi_cycle_collection,
            has_decrease=True,
            decrease_type="continuous_only",
        )

        # both
        both_result = create_skeleton_curve(
            self.multi_cycle_collection, has_decrease=True, decrease_type="both"
        )

        # それぞれ結果が異なることを確認
        env_len = len(envelope_result["load_skeleton"].values)
        cont_len = len(continuous_result["load_skeleton"].values)
        both_len = len(both_result["load_skeleton"].values)

        # 少なくとも一つは異なる長さになるはず
        assert env_len != cont_len or env_len != both_len or cont_len != both_len

    def test_create_cumulative_curve_basic(self):
        """create_cumulative_curve関数の基本機能テスト"""
        # 累積曲線を作成
        result = create_cumulative_curve(self.multi_cycle_collection)

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列の存在を確認
        assert "load_cumulative" in result.columns
        assert "displacement_cumulative" in result.columns

        # 累積曲線の値を取得
        p_cum = result["load_cumulative"].values
        d_cum = result["displacement_cumulative"].values

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

    def test_create_cumulative_curve_custom_names(self):
        """カスタムカラム名での create_cumulative_curve 関数のテスト"""
        # カスタム出力カラム名を指定して累積曲線を作成
        result = create_cumulative_curve(
            self.multi_cycle_collection,
            result_load_column="load_cum",
            result_disp_column="disp_cum",
        )

        # カスタム結果列の存在を確認
        assert "load_cum" in result.columns
        assert "disp_cum" in result.columns

        # もとのカラム名に基づく自動生成名がないことを確認
        assert "load_cumulative" not in result.columns
        assert "displacement_cumulative" not in result.columns

    def test_cycle_column_automatic_detection(self):
        """サイクル列の自動検出のテスト"""
        # サイクル列のないコレクション
        collection = ColumnCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # 荷重-変位コレクションを作成
        ld_collection_no_cycle = LoadDisplacementCollection(
            step=collection.step,
            columns=collection.columns,
            load_column="load",
            displacement_column="displacement",
        )

        # スケルトン曲線を作成（サイクル列の自動生成が行われるはず）
        skeleton_result = create_skeleton_curve(ld_collection_no_cycle)

        # 生成されたサイクル列を探す
        found_cycle_column = False
        for column_name in skeleton_result.columns:
            if (
                "cycle" in column_name.lower()
                and column_name not in ld_collection_no_cycle.columns
            ):
                found_cycle_column = True
                break

        assert found_cycle_column

        # 累積曲線についても同様にテスト
        cumulative_result = create_cumulative_curve(ld_collection_no_cycle)

        found_cycle_column = False
        for column_name in cumulative_result.columns:
            if (
                "cycle" in column_name.lower()
                and column_name not in ld_collection_no_cycle.columns
            ):
                found_cycle_column = True
                break

        assert found_cycle_column
