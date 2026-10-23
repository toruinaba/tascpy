"""荷重-変位ドメインの解析関数のテスト"""

import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.load_displacement import LoadDisplacementCollection


class TestLoadDisplacementAnalysis:
    """荷重-変位ドメインの解析関数のテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # 単調増加の荷重-変位データ（線形区間と非線形区間を含む）
        self.steps = list(range(11))
        self.loads = [0, 10, 20, 30, 40, 50, 55, 60, 63, 65, 66]  # 後半で傾きが減少
        self.displacements = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 線形

        # 基本のコレクションを作成
        collection = ColumnCollection({"load": self.loads, "displacement": self.displacements}, step=self.steps)

        # 荷重-変位コレクションを作成
        self.ld_collection = collection.ops.as_load_displacement("load", "displacement").end()

        # 降伏点テスト用に非線形データを準備（明確な降伏挙動を持つ）
        # オフセット法用に調整：初期勾配が10.0で後半は明確に低下し、オフセット線と交差する
        yield_steps = list(range(11))
        yield_loads = [
            0.0,
            10.0,
            20.0,
            30.0,
            40.0,
            45.0,
            47.0,
            48.0,
            49.0,
            49.5,
            50.0,
        ]  # 明確な傾きの変化
        yield_disps = [
            0.0,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0,
            8.0,
            9.0,
            10.0,
        ]  # 変位は均等

        yield_collection = ColumnCollection({"load": yield_loads, "displacement": yield_disps}, step=yield_steps)

        self.yield_ld_collection = yield_collection.ops.as_load_displacement("load", "displacement").end()

        # 一般降伏法用のデータセット（より早い段階で傾きが変化する）
        general_steps = list(range(11))
        general_loads = [0.0, 5.0, 10.0, 14.0, 17.0, 19.0, 20.0, 21.0, 22.0, 22.5, 23.0]
        general_disps = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

        general_collection = ColumnCollection({"load": general_loads, "displacement": general_disps}, step=general_steps)

        self.general_ld_collection = general_collection.ops.as_load_displacement("load", "displacement").end()

        # サイクルデータのセットアップ
        cycle_steps = list(range(21))
        cycle_loads = [
            0,
            10,
            20,
            30,
            35,
            30,
            20,
            10,
            0,
            -10,
            -20,
            -30,
            -35,
            -30,
            -20,
            -10,
            0,
            20,
            40,
            30,
            10,
        ]
        cycle_disps = [
            0,
            1,
            2,
            3,
            4,
            3.5,
            3,
            2.5,
            2,
            1,
            0,
            -1,
            -2,
            -1.5,
            -1,
            -0.5,
            0,
            2,
            4,
            3,
            1,
        ]

        cycle_collection = ColumnCollection({"load": cycle_loads, "displacement": cycle_disps}, step=cycle_steps)

        # サイクル荷重-変位コレクション
        self.cycle_ld_collection = cycle_collection.ops.as_load_displacement("load", "displacement").end()

        # カスタム列名のコレクション
        custom_collection = ColumnCollection({"force": self.loads, "disp": self.displacements}, step=self.steps)

        self.custom_ld_collection = custom_collection.ops.as_load_displacement("force", "disp").end()

        # エッジケースのデータ（同一変位値を含む）
        edge_steps = list(range(5))
        edge_loads = [0, 10, 20, 30, 40]
        edge_disps = [0, 1, 1, 2, 3]  # 1が重複

        edge_collection = ColumnCollection({"load": edge_loads, "displacement": edge_disps}, step=edge_steps)

        self.edge_ld_collection = edge_collection.ops.as_load_displacement("load", "displacement").end()

        # データ不足のケース
        empty_collection = ColumnCollection({"load": [], "displacement": []}, step=[])

        self.empty_ld_collection = empty_collection.ops.as_load_displacement("load", "displacement").end()

    # calculate_slopes のテスト
    def test_calculate_slopes_basic(self):
        """calculate_slopesの基本機能テスト"""
        # 傾き計算を実行
        result = self.ld_collection.ops.calculate_slopes().end()

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列の存在を確認
        expected_column = "slope_data"
        assert expected_column in result.columns

        # 傾きの値を確認
        slopes = result[expected_column].values

        # 最初の点は傾きがNaNであることを確認
        assert np.isnan(slopes[0])

        # 2番目以降の点では傾きが10であることを確認（線形データのため）
        for i in range(1, 5):
            assert slopes[i] == pytest.approx(10.0)

        # 後半の点では傾きが減少していることを確認
        assert slopes[-1] < 10.0

    def test_calculate_slopes_custom_columns(self):
        """カスタム列名でのcalculate_slopes機能テスト"""
        # カスタム列名のコレクションで傾き計算を実行
        result = self.custom_ld_collection.ops.calculate_slopes().end()

        # 結果列の存在を確認
        expected_column = "slope_data"
        assert expected_column in result.columns

        # 傾きの値を確認
        slopes = result[expected_column].values

        # 最初の点は傾きがNaNであることを確認
        assert np.isnan(slopes[0])

        # 2番目以降の点では傾きが10であることを確認（線形データのため）
        for i in range(1, 5):
            assert slopes[i] == pytest.approx(10.0)

    def test_calculate_slopes_result_column(self):
        """結果カラム名を指定したcalculate_slopes機能テスト"""
        # 結果カラム名を指定して傾き計算を実行
        custom_column = "my_slopes"
        result = self.ld_collection.ops.calculate_slopes(result_column=custom_column).end()

        # 指定した結果列の存在を確認
        assert custom_column in result.columns

        # デフォルト列名が存在しないことを確認
        default_column = "slope_data"
        assert default_column not in result.columns

        # 傾きの値を確認
        slopes = result[custom_column].values

        # 最初の点は傾きがNaNであることを確認
        assert np.isnan(slopes[0])

        # 2番目以降の点では傾きが10であることを確認
        for i in range(1, 5):
            assert slopes[i] == pytest.approx(10.0)

    def test_calculate_slopes_edge_cases(self):
        """エッジケースでのcalculate_slopes機能テスト（xの値が同じケースなど）"""
        # エッジケースのコレクションで傾き計算を実行
        result = self.edge_ld_collection.ops.calculate_slopes().end()

        # 結果列の存在を確認
        expected_column = "slope_data"
        assert expected_column in result.columns

        # 傾きの値を確認
        slopes = result[expected_column].values

        # 最初の点は傾きがNaNであることを確認
        assert np.isnan(slopes[0])

        # xの値が変わらない点では傾きがNaNであることを確認（インデックス2の点）
        assert np.isnan(slopes[2])

    # calculate_stiffness のテスト
    def test_calculate_stiffness_linear_regression(self):
        """線形回帰法によるcalculate_stiffnessのテスト"""
        # デフォルトは線形回帰法
        result = self.ld_collection.ops.calculate_stiffness(
            range_start=0.2,  # 荷重最大値の20%から
            range_end=0.8,  # 荷重最大値の80%まで
            method="linear_regression",
        ).end()

        assert isinstance(result, LoadDisplacementCollection)
        assert "stiffness" in result.results
        # 線形データの傾きは10程度になるはず
        assert result.results["stiffness"].value == pytest.approx(10.0, rel=0.1)

    def test_calculate_stiffness_secant(self):
        """割線法によるcalculate_stiffnessのテスト"""
        # 割線法で剛性を計算
        result = self.ld_collection.ops.calculate_stiffness(
            range_start=0.2,  # 荷重最大値の20%から
            range_end=0.8,  # 荷重最大値の80%まで
            method="secant",
        ).end()

        # 線形データの傾きは10程度になるはず（割線法でも同様）
        assert result.results["stiffness"].value == pytest.approx(10.0, rel=0.1)

        # サイクルデータで計算
        cycle_result = self.cycle_ld_collection.ops.calculate_stiffness(range_start=0.2, range_end=0.8, method="secant").end()

        # サイクルデータでも妥当な値になることを確認
        assert cycle_result.results["stiffness"].value != 0

    def test_calculate_stiffness_range(self):
        """異なる範囲でのcalculate_stiffnessのテスト"""
        # 範囲を変えて剛性を計算
        result1 = self.ld_collection.ops.calculate_stiffness(
            range_start=0.1,  # 荷重最大値の10%から
            range_end=0.5,  # 荷重最大値の50%まで
        ).end()

        result2 = self.ld_collection.ops.calculate_stiffness(
            range_start=0.5,  # 荷重最大値の50%から
            range_end=0.9,  # 荷重最大値の90%まで
        ).end()

        stiffness1 = result1.results["stiffness"].value
        stiffness2 = result2.results["stiffness"].value

        # 線形部分の範囲なら剛性は同じになるはず
        assert stiffness1 == pytest.approx(10.0, rel=0.1)

        # 後半の非線形部分を含む範囲では剛性が少し変わるはず
        assert stiffness2 != pytest.approx(stiffness1, rel=0.01)

    def test_calculate_stiffness_insufficient_data(self):
        """データ不足時のcalculate_stiffnessエラーテスト"""
        # 空のコレクションで剛性計算を実行
        with pytest.raises(ValueError):
            self.empty_ld_collection.ops.calculate_stiffness().end()

        # 範囲外のデータで剛性計算を実行
        with pytest.raises(ValueError):
            self.ld_collection.ops.calculate_stiffness(
                range_start=0.9,  # 荷重最大値の90%から
                range_end=0.95,  # 荷重最大値の95%まで（このデータ範囲には点が少ない）
            ).end()

    # find_yield_point のテスト
    def test_find_yield_point_offset(self):
        """オフセット法によるfind_yield_pointのテスト"""
        # オフセット法で降伏点を計算 (降伏挙動を持つデータコレクションを使用)
        result = self.yield_ld_collection.ops.find_yield_point(
            method="offset",
            offset_value=0.002,
            range_start=0.0,  # 範囲開始を0%に設定（データのはじめから）
            range_end=0.6,  # 範囲終了を60%に設定（線形領域内）
            ).end()

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列の存在を確認
        assert "yield_point" in result.results
        

        # 降伏変位と荷重の値が数値であることを確認
        yield_disp = result.results["yield_point"].x
        yield_load = result.results["yield_point"].y

        assert isinstance(yield_disp, (int, float))
        assert isinstance(yield_load, (int, float))

    def test_find_yield_point_general(self):
        """一般降伏法によるfind_yield_pointのテスト"""
        # 一般降伏法で降伏点を計算 (降伏挙動を持つデータコレクションを使用)
        result = self.yield_ld_collection.ops.find_yield_point(
            method="general",
            factor=0.33,
            range_start=0.0,  # 範囲開始を0%に設定（データのはじめから）
            range_end=0.6,  # 範囲終了を60%に設定（線形領域内）
            ).end()

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列の存在を確認
        assert "yield_point" in result.results
        

        # 降伏変位と荷重の値が数値であることを確認
        yield_disp = result.results["yield_point"].x
        yield_load = result.results["yield_point"].y

        assert isinstance(yield_disp, (int, float))
        assert isinstance(yield_load, (int, float))

        # オフセット法との結果の違いを確認
        offset_result = self.yield_ld_collection.ops.find_yield_point(
            method="offset",
            offset_value=0.002,
            range_start=0.0,  # 範囲開始を0%に設定
            range_end=0.6,  # 範囲終了を60%に設定
            ).end()

        offset_disp = offset_result.results["yield_point"].x
        general_disp = result.results["yield_point"].x

        # 2つの方法での結果は異なるはず
        assert offset_disp != pytest.approx(general_disp)

    def test_find_yield_point_metadata(self):
        """find_yield_pointのメタデータ設定テスト"""
        # 降伏点を計算
        result = self.yield_ld_collection.ops.find_yield_point(
            method="offset",
            offset_value=0.002,
            range_start=0.0,  # 範囲開始を0%に設定
            range_end=0.6,  # 範囲終了を60%に設定
        ).end()

        # メタデータに降伏点情報が追加されていることを確認
        assert "yield_point" in result.results
        assert "is_valid" in result.results["yield_point"].metadata

        # メタデータの内容を確認
        yield_data = result.results["yield_point"].metadata

        assert "offset_value" in yield_data
        assert "offset_amount" in yield_data
        assert "diff_stats" in yield_data

    def test_find_yield_point_insufficient_data(self):
        """データ不足時のfind_yield_pointエラーテスト"""
        # 空のコレクションで降伏点計算を実行
        with pytest.raises(ValueError):
            self.empty_ld_collection.ops.find_yield_point().end()

    def test_find_yield_point_no_yield(self):
        """降伏点が見つからない場合のエラーテスト"""
        # 完全に線形なデータを作成（降伏点が見つからない）
        steps = list(range(5))
        loads = [0, 25, 50, 75, 100]  # 完全に線形
        disps = [0, 5, 10, 15, 20]  # 完全に線形

        linear_collection = ColumnCollection({"load": loads, "displacement": disps}, step=steps)

        linear_ld_collection = linear_collection.ops.as_load_displacement("load", "displacement").end()

        # 一般降伏法では降伏点が見つからないはず
        with pytest.raises(ValueError):
            linear_ld_collection.ops.find_yield_point(
                method="general",
                factor=0.1,  # 非常に小さな係数（傾きが変わらないデータでは降伏点が見つからない）
            ).end()
