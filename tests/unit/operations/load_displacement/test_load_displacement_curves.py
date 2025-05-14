"""荷重-変位ドメインの曲線生成関数のテスト"""

import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column, NumberColumn
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.operations.load_displacement.curves import (
    create_skeleton_curve,
    create_cumulative_curve,
    get_curve_data,
    get_curve_columns,
    list_available_curves,
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
        # スケルトン曲線を作成（旧形式との互換性モードで実行）
        result = create_skeleton_curve(self.ld_collection, store_as_columns=True)

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

    def test_create_skeleton_curve_metadata(self):
        """create_skeleton_curve関数のメタデータ格納機能のテスト"""
        # スケルトン曲線をメタデータに格納するモードで作成（デフォルト）
        result = create_skeleton_curve(self.ld_collection)

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列が作成されていないことを確認
        assert "load_skeleton" not in result.columns
        assert "displacement_skeleton" not in result.columns

        # メタデータにカーブデータが格納されていることを確認
        assert result.metadata is not None
        assert "curves" in result.metadata
        assert "skeleton_curve" in result.metadata["curves"]

        # カーブデータの構造を確認
        curve_data = result.metadata["curves"]["skeleton_curve"]
        assert "x" in curve_data
        assert "y" in curve_data
        assert "metadata" in curve_data

        # メタデータの内容を確認
        curve_metadata = curve_data["metadata"]
        assert "source_columns" in curve_metadata
        assert "description" in curve_metadata
        assert "units" in curve_metadata
        assert "parameters" in curve_metadata

        # 元のデータとの整合性を確認
        assert curve_metadata["source_columns"]["load"] == "load"
        assert curve_metadata["source_columns"]["displacement"] == "displacement"

        # データポイントの存在を確認
        assert len(curve_data["x"]) > 0
        assert len(curve_data["y"]) > 0
        assert len(curve_data["x"]) == len(curve_data["y"])

        # 最大荷重が含まれることを確認
        assert max(self.loads) in curve_data["y"]

    def test_create_skeleton_curve_custom_names(self):
        """カスタムカラム名での create_skeleton_curve 関数のテスト"""
        # カスタム出力カラム名を指定してスケルトン曲線を作成
        result = create_skeleton_curve(
            self.custom_ld_collection,
            result_load_column="force_skl",
            result_disp_column="disp_skl",
            store_as_columns=True,
        )

        # カスタム結果列の存在を確認
        assert "force_skl" in result.columns
        assert "disp_skl" in result.columns

        # もとのカラム名に基づく自動生成名がないことを確認
        assert "force_skeleton" not in result.columns
        assert "disp_skeleton" not in result.columns

        # メタデータも正しく格納されていることを確認
        assert "skeleton_curve" in result.metadata["curves"]
        assert (
            result.metadata["curves"]["skeleton_curve"]["metadata"]["source_columns"][
                "load"
            ]
            == "force"
        )

    def test_create_skeleton_curve_with_decrease(self):
        """減少部分を含むスケルトン曲線のテスト"""
        # 複数サイクルの場合
        result = create_skeleton_curve(
            self.multi_cycle_collection,
            has_decrease=True,
            decrease_type="envelope",
            store_as_columns=True,
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
            self.multi_cycle_collection,
            has_decrease=True,
            decrease_type="envelope",
            store_as_columns=True,
        )

        # continuous_only
        continuous_result = create_skeleton_curve(
            self.multi_cycle_collection,
            has_decrease=True,
            decrease_type="continuous_only",
            store_as_columns=True,
        )

        # both
        both_result = create_skeleton_curve(
            self.multi_cycle_collection,
            has_decrease=True,
            decrease_type="both",
            store_as_columns=True,
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
        result = create_cumulative_curve(
            self.multi_cycle_collection, store_as_columns=True
        )

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

    def test_create_cumulative_curve_metadata(self):
        """create_cumulative_curve関数のメタデータ格納機能のテスト"""
        # 累積曲線をメタデータに格納するモードで作成（デフォルト）
        result = create_cumulative_curve(self.multi_cycle_collection)

        # 結果のコレクション型の確認
        assert isinstance(result, LoadDisplacementCollection)

        # 結果列が作成されていないことを確認
        assert "load_cumulative" not in result.columns
        assert "displacement_cumulative" not in result.columns

        # メタデータにカーブデータが格納されていることを確認
        assert result.metadata is not None
        assert "curves" in result.metadata
        assert "cumulative_curve" in result.metadata["curves"]

        # カーブデータの構造を確認
        curve_data = result.metadata["curves"]["cumulative_curve"]
        assert "x" in curve_data
        assert "y" in curve_data
        assert "metadata" in curve_data

        # メタデータの内容を確認
        curve_metadata = curve_data["metadata"]
        assert "source_columns" in curve_metadata
        assert "description" in curve_metadata
        assert "units" in curve_metadata

        # 元のデータとの整合性を確認
        assert curve_metadata["source_columns"]["load"] == "load"
        assert curve_metadata["source_columns"]["displacement"] == "displacement"

        # データポイントの存在を確認
        assert len(curve_data["x"]) > 0
        assert len(curve_data["y"]) > 0
        assert len(curve_data["x"]) == len(curve_data["y"])

    def test_create_cumulative_curve_custom_names(self):
        """カスタムカラム名での create_cumulative_curve 関数のテスト"""
        # カスタム出力カラム名を指定して累積曲線を作成
        result = create_cumulative_curve(
            self.multi_cycle_collection,
            result_load_column="load_cum",
            result_disp_column="disp_cum",
            store_as_columns=True,
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

    def test_get_curve_data(self):
        """get_curve_data関数のテスト"""
        # スケルトン曲線と累積曲線を作成
        result = create_skeleton_curve(self.ld_collection)
        result = create_cumulative_curve(result)

        # スケルトン曲線データを取得
        skeleton_data = get_curve_data(result, "skeleton_curve")

        # データ構造と内容を確認
        assert "x" in skeleton_data
        assert "y" in skeleton_data
        assert "metadata" in skeleton_data
        assert len(skeleton_data["x"]) > 0
        assert len(skeleton_data["y"]) > 0

        # 累積曲線データを取得
        cumulative_data = get_curve_data(result, "cumulative_curve")

        # データ構造と内容を確認
        assert "x" in cumulative_data
        assert "y" in cumulative_data
        assert "metadata" in cumulative_data
        assert len(cumulative_data["x"]) > 0
        assert len(cumulative_data["y"]) > 0

        # 存在しない曲線名での例外発生テスト
        with pytest.raises(ValueError):
            get_curve_data(result, "nonexistent_curve")

    def test_list_available_curves(self):
        """list_available_curves関数のテスト"""
        # 曲線がないコレクション
        empty_result = list_available_curves(self.ld_collection)
        assert len(empty_result) == 0

        # スケルトン曲線のみ作成
        skeleton_result = create_skeleton_curve(self.ld_collection)
        curve_list = list_available_curves(skeleton_result)
        assert len(curve_list) == 1
        assert "skeleton_curve" in curve_list

        # スケルトン曲線と累積曲線を作成
        both_result = create_cumulative_curve(skeleton_result)
        curve_list = list_available_curves(both_result)
        assert len(curve_list) == 2
        assert "skeleton_curve" in curve_list
        assert "cumulative_curve" in curve_list

    def test_store_as_columns_parameter(self):
        """store_as_columns パラメータのテスト"""
        # メタデータのみに格納（デフォルト）
        metadata_only = create_skeleton_curve(
            self.ld_collection, store_as_columns=False
        )
        assert "load_skeleton" not in metadata_only.columns
        assert "displacement_skeleton" not in metadata_only.columns
        assert "skeleton_curve" in metadata_only.metadata["curves"]

        # 列とメタデータの両方に格納
        both_storage = create_skeleton_curve(self.ld_collection, store_as_columns=True)
        assert "load_skeleton" in both_storage.columns
        assert "displacement_skeleton" in both_storage.columns
        assert "skeleton_curve" in both_storage.metadata["curves"]

        # メタデータと列のデータが一致していることを確認
        col_x = both_storage["displacement_skeleton"].values
        col_y = both_storage["load_skeleton"].values
        meta_x = both_storage.metadata["curves"]["skeleton_curve"]["x"]
        meta_y = both_storage.metadata["curves"]["skeleton_curve"]["y"]

        assert len(col_x) == len(meta_x)
        assert len(col_y) == len(meta_y)
        for i in range(len(col_x)):
            assert col_x[i] == meta_x[i]
            assert col_y[i] == meta_y[i]

    def test_get_curve_columns(self):
        """get_curve_columns関数のテスト"""
        # スケルトン曲線と累積曲線を作成
        result = create_skeleton_curve(self.ld_collection)
        result = create_cumulative_curve(result)

        # スケルトン曲線のColumnオブジェクトを取得
        disp_col, load_col = get_curve_columns(result, "skeleton_curve")

        # Columnオブジェクトの型確認
        assert isinstance(disp_col, NumberColumn)
        assert isinstance(load_col, NumberColumn)

        # Columnオブジェクトの内容確認
        assert disp_col.name == "skeleton_curve_disp"
        assert load_col.name == "skeleton_curve_load"

        # 値の存在確認
        assert len(disp_col.values) > 0
        assert len(load_col.values) > 0

        # メタデータの確認
        assert "description" in disp_col.metadata
        assert "source_column" in disp_col.metadata
        assert disp_col.metadata["source_column"] == "displacement"
        assert load_col.metadata["source_column"] == "load"

        # 単位の確認
        assert disp_col.unit == (
            self.ld_collection["displacement"].unit
            if hasattr(self.ld_collection["displacement"], "unit")
            else None
        )
        assert load_col.unit == (
            self.ld_collection["load"].unit
            if hasattr(self.ld_collection["load"], "unit")
            else None
        )

        # 累積曲線のColumnオブジェクトも取得
        disp_col_cum, load_col_cum = get_curve_columns(result, "cumulative_curve")

        # 基本情報の確認
        assert isinstance(disp_col_cum, NumberColumn)
        assert isinstance(load_col_cum, NumberColumn)
        assert disp_col_cum.name == "cumulative_curve_disp"
        assert load_col_cum.name == "cumulative_curve_load"

        # 存在しない曲線名での例外発生テスト
        with pytest.raises(ValueError):
            get_curve_columns(result, "nonexistent_curve")

        # メタデータにcolumnsキーがない古い形式の場合のテスト
        # メタデータの構造を変更して古い形式をシミュレート
        old_format_result = result.clone()
        old_format_result.metadata["curves"]["test_curve"] = {
            "x": [0, 1, 2],
            "y": [0, 10, 20],
            "metadata": {"description": "テスト用曲線"},
        }

        # Columnsキーがない曲線でget_curve_columnsを呼び出すと例外が発生するはず
        with pytest.raises(ValueError) as exc_info:
            get_curve_columns(old_format_result, "test_curve")

        # 例外メッセージの確認
        assert "Columnデータが含まれていません" in str(exc_info.value)
