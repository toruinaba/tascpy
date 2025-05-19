"""荷重-変位ドメインのユーティリティ関数のテスト"""

import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.operations.load_displacement.utils import (
    get_load_column,
    get_displacement_column,
    get_load_data,
    get_displacement_data,
    get_valid_data_mask,
    get_valid_data,
)


class TestLoadDisplacementUtils:
    """荷重-変位ドメインのユーティリティ関数のテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # 基本的な荷重-変位データを作成（None値を含む）
        self.steps = list(range(6))
        self.loads = [0, 10, None, -10, 0, 20]
        self.displacements = [0, 1, 0, -1, None, 2]

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

    def test_get_load_column(self):
        """get_load_column関数のテスト"""
        # デフォルトのカラム名の場合
        load_column = get_load_column(self.ld_collection)
        assert load_column == "load"

        # カスタムカラム名の場合
        load_column = get_load_column(self.custom_ld_collection)
        assert load_column == "force"

    def test_get_displacement_column(self):
        """get_displacement_column関数のテスト"""
        # デフォルトのカラム名の場合
        disp_column = get_displacement_column(self.ld_collection)
        assert disp_column == "displacement"

        # カスタムカラム名の場合
        disp_column = get_displacement_column(self.custom_ld_collection)
        assert disp_column == "disp"

    def test_get_load_data(self):
        """get_load_data関数のテスト"""
        # 荷重データの取得
        load_data = get_load_data(self.ld_collection)

        # 型と要素数の確認
        assert isinstance(load_data, np.ndarray)
        assert len(load_data) == len(self.loads)

        # None値がnanに変換されていることを確認
        assert np.isnan(load_data[2])  # Noneは np.nan に変換される

        # 通常の値は保持されていることを確認
        assert load_data[0] == self.loads[0]
        assert load_data[1] == self.loads[1]
        assert load_data[3] == self.loads[3]
        assert load_data[4] == self.loads[4]
        assert load_data[5] == self.loads[5]

        # カスタムカラム名の場合も同様
        custom_load_data = get_load_data(self.custom_ld_collection)
        assert np.isnan(custom_load_data[2])
        assert custom_load_data[1] == self.loads[1]

    def test_get_displacement_data(self):
        """get_displacement_data関数のテスト"""
        # 変位データの取得
        disp_data = get_displacement_data(self.ld_collection)

        # 型と要素数の確認
        assert isinstance(disp_data, np.ndarray)
        assert len(disp_data) == len(self.displacements)

        # None値がnanに変換されていることを確認
        assert np.isnan(disp_data[4])  # Noneは np.nan に変換される

        # 通常の値は保持されていることを確認
        assert disp_data[0] == self.displacements[0]
        assert disp_data[1] == self.displacements[1]
        assert disp_data[2] == self.displacements[2]
        assert disp_data[3] == self.displacements[3]
        assert disp_data[5] == self.displacements[5]

        # カスタムカラム名の場合も同様
        custom_disp_data = get_displacement_data(self.custom_ld_collection)
        assert np.isnan(custom_disp_data[4])
        assert custom_disp_data[1] == self.displacements[1]

    def test_get_valid_data_mask(self):
        """get_valid_data_mask関数のテスト"""
        # 有効なデータのマスクを取得
        mask = get_valid_data_mask(self.ld_collection)

        # 型と要素数の確認
        assert isinstance(mask, np.ndarray)
        assert len(mask) == len(self.loads)

        # マスクの値の確認：None値がない場所はTrue、ある場所はFalse
        # index 0: load=0, disp=0 -> True
        # index 1: load=10, disp=1 -> True
        # index 2: load=None, disp=0 -> False
        # index 3: load=-10, disp=-1 -> True
        # index 4: load=0, disp=None -> False
        # index 5: load=20, disp=2 -> True
        expected_mask = np.array([True, True, False, True, False, True])
        assert np.array_equal(mask, expected_mask)

    def test_get_valid_data(self):
        """get_valid_data関数のテスト"""
        # 有効なデータを取得
        disp_data, load_data = get_valid_data(self.ld_collection)

        # 型と要素数の確認
        assert isinstance(disp_data, np.ndarray)
        assert isinstance(load_data, np.ndarray)
        assert len(disp_data) == len(load_data)

        # None値が除外されていることを確認
        # index 0: load=0, disp=0
        # index 1: load=10, disp=1
        # index 3: load=-10, disp=-1
        # index 5: load=20, disp=2
        expected_disp = np.array([0, 1, -1, 2])
        expected_load = np.array([0, 10, -10, 20])

        assert np.array_equal(disp_data, expected_disp)
        assert np.array_equal(load_data, expected_load)
