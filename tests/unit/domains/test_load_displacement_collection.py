"""荷重-変位ドメインのコレクションクラスのテスト"""

import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection


class TestLoadDisplacementCollection:
    """荷重-変位ドメインのコレクションクラスのテスト"""

    def setup_method(self):
        """各テスト前に実行される前処理"""
        # 基本的な荷重-変位データを作成
        self.steps = list(range(5))
        self.loads = [0.0, 10.0, 20.0, 15.0, 5.0]
        self.displacements = [0.0, 0.1, 0.2, 0.15, 0.05]

        # 基本のコレクションを作成
        self.collection = ColumnCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

    def test_initialization(self):
        """基本的な初期化のテスト"""
        # LoadDisplacementCollectionを直接初期化
        ld_collection = LoadDisplacementCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # プロパティが正しく設定されていることを確認
        assert ld_collection.load_column == "load"
        assert ld_collection.displacement_column == "displacement"
        assert list(ld_collection["load"].values) == self.loads
        assert list(ld_collection["displacement"].values) == self.displacements

        # ドメイン情報が正しく設定されていることを確認
        assert ld_collection.domain == "load_displacement"

    def test_initialization_custom_columns(self):
        """カスタムカラム名での初期化テスト"""
        # 異なるカラム名を使用して初期化
        columns = {"force": self.loads, "disp": self.displacements}
        ld_collection = LoadDisplacementCollection(
            self.steps, columns, load_column="force", displacement_column="disp"
        )

        # カスタムカラム名が正しく設定されていることを確認
        assert ld_collection.load_column == "force"
        assert ld_collection.displacement_column == "disp"
        assert list(ld_collection["force"].values) == self.loads
        assert list(ld_collection["disp"].values) == self.displacements

    def test_from_collection(self):
        """通常のコレクションからの変換テスト"""
        # ops.as_domain()を使用してドメインコレクションに変換
        ld_collection = self.collection.ops.as_domain("load_displacement").end()

        # 型と内容を確認
        assert isinstance(ld_collection, LoadDisplacementCollection)
        assert ld_collection.load_column == "load"
        assert ld_collection.displacement_column == "displacement"
        assert list(ld_collection["load"].values) == self.loads

    def test_from_collection_custom_columns(self):
        """カスタムカラム名を指定した変換テスト"""
        # カスタムデータを作成
        collection = ColumnCollection(
            self.steps, {"force": self.loads, "disp": self.displacements}
        )

        # カラム名を明示的に指定して変換
        ld_collection = collection.ops.as_domain(
            "load_displacement", load_column="force", displacement_column="disp"
        ).end()

        # 設定が正しいことを確認
        assert isinstance(ld_collection, LoadDisplacementCollection)
        assert ld_collection.load_column == "force"
        assert ld_collection.displacement_column == "disp"

    def test_clone(self):
        """クローン操作のテスト"""
        # 元のLoadDisplacementCollectionを作成
        original = LoadDisplacementCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # クローンを作成
        cloned = original.clone()

        # クローンがLoadDisplacementCollectionであることを確認
        assert isinstance(cloned, LoadDisplacementCollection)

        # ドメイン固有のプロパティが保持されていることを確認
        assert cloned.load_column == original.load_column
        assert cloned.displacement_column == original.displacement_column

        # データが同じであることを確認
        assert list(cloned["load"].values) == list(original["load"].values)
        assert list(cloned["displacement"].values) == list(
            original["displacement"].values
        )

        # 別のオブジェクトであることを確認
        assert cloned is not original

        # クローンの変更が元に影響しないことを確認
        cloned["load"].values[0] = 100.0
        assert original["load"].values[0] == 0.0

    def test_missing_columns(self):
        """必要なカラムがない場合のエラーテスト"""
        # 荷重カラムのみを持つコレクション
        load_only = ColumnCollection(self.steps, {"load": self.loads})

        # 変位カラムがないためエラーになるはず
        with pytest.raises(ValueError) as exc_info:
            load_only.ops.as_domain("load_displacement").end()

        assert "displacement_column" in str(exc_info.value)

        # 変位カラムのみを持つコレクション
        disp_only = ColumnCollection(self.steps, {"displacement": self.displacements})

        # 荷重カラムがないためエラーになるはず
        with pytest.raises(ValueError) as exc_info:
            disp_only.ops.as_domain("load_displacement").end()

        assert "load_column" in str(exc_info.value)

    def test_direct_invalid_columns(self):
        """直接初期化時の無効なカラム指定テスト"""
        # 存在しないカラムを指定
        with pytest.raises(ValueError) as exc_info:
            LoadDisplacementCollection(
                self.steps,
                {"load": self.loads, "displacement": self.displacements},
                load_column="nonexistent",
                displacement_column="displacement",
            )

        assert "load_column" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            LoadDisplacementCollection(
                self.steps,
                {"load": self.loads, "displacement": self.displacements},
                load_column="load",
                displacement_column="nonexistent",
            )

        assert "displacement_column" in str(exc_info.value)

    def test_default_operations(self):
        """デフォルト操作が利用可能かテスト"""
        # LoadDisplacementCollectionを作成
        ld_collection = LoadDisplacementCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # コアドメインの操作が使用可能であることを確認
        ops = ld_collection.ops

        # いくつかのコア操作をテスト
        filtered = ops.filter_by_value("load", 10.0).end()
        assert len(filtered) == 1
        assert filtered["load"].values[0] == 10.0

        added = ops.add("load", 5.0).end()
        assert added["load+5.0"].values[0] == 5.0  # 元の0.0 + 5.0

        # 特定の行のみを選択
        selected = ops.select_step(steps=[1, 2]).end()
        assert len(selected) == 2
        assert selected.step.values == [1, 2]

    def test_domain_operations(self):
        """ドメイン固有の操作が利用可能かテスト"""
        # LoadDisplacementCollectionを作成
        ld_collection = LoadDisplacementCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # 操作プロキシを取得
        ops = ld_collection.ops

        # ドメイン固有の操作が存在することを確認
        # このテストは実際のドメイン操作が実装された後に更新する必要がある
        # 例えば、calculate_stiffness、find_yield_point_offsetなど

        # とりあえず操作プロキシのドメインが正しいことを確認
        assert ops._domain == "load_displacement"

    def test_getitem_basic_access(self):
        """__getitem__メソッドの基本アクセステスト"""
        # LoadDisplacementCollectionを作成
        ld_collection = LoadDisplacementCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # 通常のカラムアクセスが機能することを確認
        assert list(ld_collection["load"].values) == self.loads
        assert list(ld_collection["displacement"].values) == self.displacements

        # ショートカットアクセスの確認
        assert list(ld_collection["load"].values) == list(
            ld_collection[ld_collection.load_column].values
        )
        assert list(ld_collection["displacement"].values) == list(
            ld_collection[ld_collection.displacement_column].values
        )

    def test_getitem_metadata_access(self):
        """__getitem__メソッドのメタデータアクセステスト"""
        # LoadDisplacementCollectionを作成
        ld_collection = LoadDisplacementCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # 曲線データを持つメタデータを追加
        ld_collection.metadata["curves"] = {
            "skeleton_curve": {
                "x": [0.0, 0.1, 0.2],
                "y": [0.0, 10.0, 20.0],
                "metadata": {
                    "source_columns": ["load", "displacement"],
                    "description": "スケルトン曲線",
                },
                "columns": {
                    "x": ld_collection["displacement"].clone(),
                    "y": ld_collection["load"].clone(),
                },
            }
        }

        # 曲線データにアクセス
        assert ld_collection["curves"] == ld_collection.metadata["curves"]
        assert (
            ld_collection["skeleton_curve"]
            == ld_collection.metadata["curves"]["skeleton_curve"]
        )

        # ドット記法によるアクセス
        assert (
            ld_collection["curves.skeleton_curve"]
            == ld_collection.metadata["curves"]["skeleton_curve"]
        )
        assert (
            ld_collection["curves.skeleton_curve.x"]
            == ld_collection.metadata["curves"]["skeleton_curve"]["x"]
        )
        assert (
            ld_collection["curves.skeleton_curve.y"]
            == ld_collection.metadata["curves"]["skeleton_curve"]["y"]
        )

        # より深いレベルへのアクセス
        assert (
            ld_collection["curves.skeleton_curve.metadata.description"]
            == "スケルトン曲線"
        )
        assert (
            ld_collection["curves.skeleton_curve.metadata.source_columns.0"] == "load"
        )
        assert (
            ld_collection["curves.skeleton_curve.metadata.source_columns.1"]
            == "displacement"
        )

        # カラムオブジェクトへのアクセス
        assert isinstance(
            ld_collection["curves.skeleton_curve.columns.x"],
            type(ld_collection["displacement"]),
        )
        assert isinstance(
            ld_collection["curves.skeleton_curve.columns.y"],
            type(ld_collection["load"]),
        )

    def test_getitem_error_handling(self):
        """__getitem__メソッドのエラーハンドリングテスト"""
        # LoadDisplacementCollectionを作成
        ld_collection = LoadDisplacementCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # メタデータがない状態での"curves"アクセス
        # curves キーがなくてもエラーにならないことを確認
        assert ld_collection["curves"] == {}

        # 存在しないカラムへのアクセスでKeyErrorが発生することを確認
        with pytest.raises(KeyError) as exc_info:
            _ = ld_collection["nonexistent_column"]
        assert "nonexistent_column" in str(exc_info.value)

        # 存在しないパスへのアクセスでKeyErrorが発生することを確認
        with pytest.raises(KeyError) as exc_info:
            _ = ld_collection["curves.nonexistent_curve"]
        assert "curves" in str(exc_info.value) or "nonexistent_curve" in str(
            exc_info.value
        )

        # 不正なパスへのアクセスでKeyErrorが発生することを確認
        with pytest.raises(KeyError) as exc_info:
            _ = ld_collection["load.invalid.path"]
        assert "invalid" in str(exc_info.value) or "path" in str(exc_info.value)

    def test_getitem_with_complex_curve_data(self):
        """複雑な曲線データがある場合の__getitem__メソッドテスト"""
        # LoadDisplacementCollectionを作成
        ld_collection = LoadDisplacementCollection(
            self.steps, {"load": self.loads, "displacement": self.displacements}
        )

        # 複数の曲線データを含むメタデータを追加
        ld_collection.metadata["curves"] = {
            "skeleton_curve": {
                "x": [0.0, 0.1, 0.2],
                "y": [0.0, 10.0, 20.0],
                "parameters": {"method": "envelope", "has_decrease": False},
            },
            "cumulative_curve": {
                "x": [0.0, 0.2, 0.4, 0.6],
                "y": [0.0, 20.0, 30.0, 40.0],
                "parameters": {"method": "cumulative", "cycle_column": "cycle"},
            },
        }

        # 異なる曲線データへのアクセス
        assert ld_collection["skeleton_curve"]["x"][1] == 0.1
        assert ld_collection["cumulative_curve"]["y"][2] == 30.0

        # ドット記法による複数の曲線データへのアクセス
        assert ld_collection["curves.skeleton_curve.parameters.method"] == "envelope"
        assert (
            ld_collection["curves.cumulative_curve.parameters.cycle_column"] == "cycle"
        )

        # 短縮形でのアクセス
        assert ld_collection["skeleton_curve"] == ld_collection["curves.skeleton_curve"]
        assert (
            ld_collection["cumulative_curve"]
            == ld_collection["curves.cumulative_curve"]
        )
