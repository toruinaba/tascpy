"""荷重-変位ドメインの解析関数のテスト"""

import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.operations.load_displacement.analysis import (
    calculate_slopes,
    calculate_stiffness,
    find_yield_point,
)


class TestLoadDisplacementAnalysis:
    """荷重-変位ドメインの解析関数のテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # 単調増加の荷重-変位データ（線形区間と非線形区間を含む）
        self.steps = list(range(11))
        self.loads = [0, 10, 20, 30, 40, 50, 55, 60, 63, 65, 66]  # 後半で傾きが減少
        self.displacements = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 線形

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

        yield_collection = ColumnCollection(
            yield_steps, {"load": yield_loads, "displacement": yield_disps}
        )

        self.yield_ld_collection = LoadDisplacementCollection(
            step=yield_collection.step,
            columns=yield_collection.columns,
            load_column="load",
            displacement_column="displacement",
        )

        # 一般降伏法用のデータセット（より早い段階で傾きが変化する）
        general_steps = list(range(11))
        general_loads = [0.0, 5.0, 10.0, 14.0, 17.0, 19.0, 20.0, 21.0, 22.0, 22.5, 23.0]
        general_disps = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

        general_collection = ColumnCollection(
            general_steps, {"load": general_loads, "displacement": general_disps}
        )

        self.general_ld_collection = LoadDisplacementCollection(
            step=general_collection.step,
            columns=general_collection.columns,
            load_column="load",
            displacement_column="displacement",
        )

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

        cycle_collection = ColumnCollection(
            cycle_steps, {"load": cycle_loads, "displacement": cycle_disps}
        )

        # サイクル荷重-変位コレクション
        self.cycle_ld_collection = LoadDisplacementCollection(
            step=cycle_collection.step,
            columns=cycle_collection.columns,
            load_column="load",
            displacement_column="displacement",
        )

        # カスタム列名のコレクション
        custom_collection = ColumnCollection(
            self.steps, {"force": self.loads, "disp": self.displacements}
        )

        self.custom_ld_collection = LoadDisplacementCollection(
            step=custom_collection.step,
            columns=custom_collection.columns,
            load_column="force",
            displacement_column="disp",
        )

        # エッジケースのデータ（同一変位値を含む）
        edge_steps = list(range(5))
        edge_loads = [0, 10, 20, 30, 40]
        edge_disps = [0, 1, 1, 2, 3]  # 1が重複

        edge_collection = ColumnCollection(
            edge_steps, {"load": edge_loads, "displacement": edge_disps}
        )

        self.edge_ld_collection = LoadDisplacementCollection(
            step=edge_collection.step,
            columns=edge_collection.columns,
            load_column="load",
            displacement_column="displacement",
        )

        # データ不足のケース
        empty_collection = ColumnCollection([], {"load": [], "displacement": []})

        self.empty_ld_collection = LoadDisplacementCollection(
            step=empty_collection.step,
            columns=empty_collection.columns,
            load_column="load",
            displacement_column="displacement",
        )

    # calculate_slopes のテスト
    def test_calculate_slopes_basic(self):
        """calculate_slopesの基本機能テスト"""
        # 傾き計算を実行
        result = calculate_slopes(self.ld_collection)

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列の存在を確認
        expected_column = "slope_load_displacement"
        assert expected_column in result.columns

        # 傾きの値を確認
        slopes = result[expected_column].values

        # 最初の点は傾きがNoneであることを確認
        assert slopes[0] is None

        # 2番目以降の点では傾きが10であることを確認（線形データのため）
        for i in range(1, 5):
            assert slopes[i] == pytest.approx(10.0)

        # 後半の点では傾きが減少していることを確認
        assert slopes[-1] < 10.0

    def test_calculate_slopes_custom_columns(self):
        """カスタム列名でのcalculate_slopes機能テスト"""
        # カスタム列名のコレクションで傾き計算を実行
        result = calculate_slopes(self.custom_ld_collection)

        # 結果列の存在を確認
        expected_column = "slope_force_disp"
        assert expected_column in result.columns

        # 傾きの値を確認
        slopes = result[expected_column].values

        # 最初の点は傾きがNoneであることを確認
        assert slopes[0] is None

        # 2番目以降の点では傾きが10であることを確認（線形データのため）
        for i in range(1, 5):
            assert slopes[i] == pytest.approx(10.0)

    def test_calculate_slopes_result_column(self):
        """結果カラム名を指定したcalculate_slopes機能テスト"""
        # 結果カラム名を指定して傾き計算を実行
        custom_column = "my_slopes"
        result = calculate_slopes(self.ld_collection, result_column=custom_column)

        # 指定した結果列の存在を確認
        assert custom_column in result.columns

        # デフォルト列名が存在しないことを確認
        default_column = "slope_load_displacement"
        assert default_column not in result.columns

        # 傾きの値を確認
        slopes = result[custom_column].values

        # 最初の点は傾きがNoneであることを確認
        assert slopes[0] is None

        # 2番目以降の点では傾きが10であることを確認
        for i in range(1, 5):
            assert slopes[i] == pytest.approx(10.0)

    def test_calculate_slopes_edge_cases(self):
        """エッジケースでのcalculate_slopes機能テスト（xの値が同じケースなど）"""
        # エッジケースのコレクションで傾き計算を実行
        result = calculate_slopes(self.edge_ld_collection)

        # 結果列の存在を確認
        expected_column = "slope_load_displacement"
        assert expected_column in result.columns

        # 傾きの値を確認
        slopes = result[expected_column].values

        # 最初の点は傾きがNoneであることを確認
        assert slopes[0] is None

        # xの値が変わらない点では傾きがNoneであることを確認（インデックス2の点）
        assert slopes[2] is None

    # calculate_stiffness のテスト
    def test_calculate_stiffness_linear_regression(self):
        """線形回帰法によるcalculate_stiffnessのテスト"""
        # デフォルトは線形回帰法
        stiffness = calculate_stiffness(
            self.ld_collection,
            range_start=0.2,  # 荷重最大値の20%から
            range_end=0.8,  # 荷重最大値の80%まで
            method="linear_regression",
        )

        # 線形データの傾きは10程度になるはず
        assert stiffness == pytest.approx(10.0, rel=0.1)

    def test_calculate_stiffness_secant(self):
        """割線法によるcalculate_stiffnessのテスト"""
        # 割線法で剛性を計算
        stiffness = calculate_stiffness(
            self.ld_collection,
            range_start=0.2,  # 荷重最大値の20%から
            range_end=0.8,  # 荷重最大値の80%まで
            method="secant",
        )

        # 線形データの傾きは10程度になるはず（割線法でも同様）
        assert stiffness == pytest.approx(10.0, rel=0.1)

        # サイクルデータで計算
        cycle_stiffness = calculate_stiffness(
            self.cycle_ld_collection, range_start=0.2, range_end=0.8, method="secant"
        )

        # サイクルデータでも妥当な値になることを確認
        assert cycle_stiffness != 0

    def test_calculate_stiffness_range(self):
        """異なる範囲でのcalculate_stiffnessのテスト"""
        # 範囲を変えて剛性を計算
        stiffness1 = calculate_stiffness(
            self.ld_collection,
            range_start=0.1,  # 荷重最大値の10%から
            range_end=0.5,  # 荷重最大値の50%まで
        )

        stiffness2 = calculate_stiffness(
            self.ld_collection,
            range_start=0.5,  # 荷重最大値の50%から
            range_end=0.9,  # 荷重最大値の90%まで
        )

        # 線形部分の範囲なら剛性は同じになるはず
        assert stiffness1 == pytest.approx(10.0, rel=0.1)

        # 後半の非線形部分を含む範囲では剛性が少し変わるはず
        assert stiffness2 != pytest.approx(stiffness1, rel=0.01)

    def test_calculate_stiffness_insufficient_data(self):
        """データ不足時のcalculate_stiffnessエラーテスト"""
        # 空のコレクションで剛性計算を実行
        with pytest.raises(ValueError):
            calculate_stiffness(self.empty_ld_collection)

        # 範囲外のデータで剛性計算を実行
        with pytest.raises(ValueError):
            calculate_stiffness(
                self.ld_collection,
                range_start=0.9,  # 荷重最大値の90%から
                range_end=0.95,  # 荷重最大値の95%まで（このデータ範囲には点が少ない）
            )

    # find_yield_point のテスト
    def test_find_yield_point_offset(self):
        """オフセット法によるfind_yield_pointのテスト"""
        # オフセット法で降伏点を計算 (降伏挙動を持つデータコレクションを使用)
        result = find_yield_point(
            self.yield_ld_collection,
            method="offset",
            offset_value=0.002,
            result_prefix="yield",
        )

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列の存在を確認
        assert "yield_displacement" in result.columns
        assert "yield_load" in result.columns

        # 降伏変位と荷重の値が数値であることを確認
        yield_disp = result["yield_displacement"].values[0]
        yield_load = result["yield_load"].values[0]

        assert isinstance(yield_disp, (int, float))
        assert isinstance(yield_load, (int, float))

    def test_find_yield_point_general(self):
        """一般降伏法によるfind_yield_pointのテスト"""
        # 一般降伏法で降伏点を計算 (降伏挙動を持つデータコレクションを使用)
        result = find_yield_point(
            self.yield_ld_collection,
            method="general",
            factor=0.33,
            result_prefix="yield",
        )

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列の存在を確認
        assert "yield_displacement" in result.columns
        assert "yield_load" in result.columns

        # 降伏変位と荷重の値が数値であることを確認
        yield_disp = result["yield_displacement"].values[0]
        yield_load = result["yield_load"].values[0]

        assert isinstance(yield_disp, (int, float))
        assert isinstance(yield_load, (int, float))

        # オフセット法との結果の違いを確認
        offset_result = find_yield_point(
            self.yield_ld_collection,
            method="offset",
            offset_value=0.002,
            result_prefix="yield",
        )

        offset_disp = offset_result["yield_displacement"].values[0]
        general_disp = result["yield_displacement"].values[0]

        # 2つの方法での結果は異なるはず
        assert offset_disp != pytest.approx(general_disp)

    def test_find_yield_point_custom_prefix(self):
        """カスタム接頭辞でのfind_yield_pointのテスト"""
        # カスタム接頭辞で降伏点を計算
        custom_prefix = "y_point"
        result = find_yield_point(
            self.yield_ld_collection,
            method="offset",
            offset_value=0.002,
            result_prefix=custom_prefix,
        )

        # カスタム結果列の存在を確認
        assert f"{custom_prefix}_displacement" in result.columns
        assert f"{custom_prefix}_load" in result.columns

        # デフォルト接頭辞の列がないことを確認
        assert "yield_displacement" not in result.columns

        # 降伏変位と荷重の値が数値であることを確認
        yield_disp = result[f"{custom_prefix}_displacement"].values[0]
        yield_load = result[f"{custom_prefix}_load"].values[0]

        assert isinstance(yield_disp, (int, float))
        assert isinstance(yield_load, (int, float))

    def test_find_yield_point_metadata(self):
        """find_yield_pointのメタデータ設定テスト"""
        # 降伏点を計算
        result = find_yield_point(
            self.yield_ld_collection, method="offset", offset_value=0.002
        )

        # メタデータに降伏点情報が追加されていることを確認
        assert "analysis" in result.metadata
        assert "yield_point" in result.metadata["analysis"]

        # メタデータの内容を確認
        yield_data = result.metadata["analysis"]["yield_point"]

        assert yield_data["method"] == "offset"
        assert "displacement" in yield_data
        assert "load" in yield_data
        assert "initial_slope" in yield_data
        assert "parameters" in yield_data
        assert "offset_value" in yield_data["parameters"]

    def test_find_yield_point_insufficient_data(self):
        """データ不足時のfind_yield_pointエラーテスト"""
        # 空のコレクションで降伏点計算を実行
        with pytest.raises(ValueError):
            find_yield_point(self.empty_ld_collection)

    def test_find_yield_point_no_yield(self):
        """降伏点が見つからない場合のエラーテスト"""
        # 完全に線形なデータを作成（降伏点が見つからない）
        steps = list(range(5))
        loads = [0, 25, 50, 75, 100]  # 完全に線形
        disps = [0, 5, 10, 15, 20]  # 完全に線形

        linear_collection = ColumnCollection(
            steps, {"load": loads, "displacement": disps}
        )

        linear_ld_collection = LoadDisplacementCollection(
            step=linear_collection.step,
            columns=linear_collection.columns,
            load_column="load",
            displacement_column="displacement",
        )

        # 一般降伏法では降伏点が見つからないはず
        with pytest.raises(ValueError):
            find_yield_point(
                linear_ld_collection,
                method="general",
                factor=0.1,  # 非常に小さな係数（傾きが変わらないデータでは降伏点が見つからない）
            )
