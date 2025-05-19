import pytest
from src.tascpy.operations.core.filters import (
    filter_by_value,
    filter_out_none,
    remove_consecutive_duplicates_across,
    remove_outliers,
)
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "A": Column("1", "Column A", "N", [1, 2, 3, 4, 5]),
            "B": Column("2", "Column B", "kg", [10, 20, 30, 40, 50]),
            "C": Column("3", "Column C", "m", [100, None, 300, None, 500]),
        },
        metadata={"description": "Test Collection"},
    )


class TestFilterByValue:
    """filter_by_value関数のテスト"""

    def test_exact_match(self, sample_collection):
        """filter_by_valueが正確に一致する値をフィルタリングできることを確認"""
        result = filter_by_value(sample_collection, "A", 3)

        # 結果の検証
        assert len(result.step) == 1
        assert result.step[0] == 3
        assert result["A"][0] == 3
        assert result["B"][0] == 30
        assert result["C"][0] == 300
        assert result.metadata == sample_collection.metadata

    def test_tolerance_filter(self, sample_collection):
        """許容範囲を使用したフィルタリングが機能することを確認"""
        result = filter_by_value(sample_collection, "A", 3, tolerance=1.0)

        # 結果の検証: 2, 3, 4 の値がフィルタリングされるはず
        assert len(result.step) == 3
        # Indicesオブジェクトの値を直接比較する代わりに個々の要素を確認
        assert result.step.values == [2, 3, 4]
        assert [result["A"][i] for i in range(3)] == [2, 3, 4]
        assert [result["B"][i] for i in range(3)] == [20, 30, 40]

    def test_no_match(self, sample_collection):
        """一致する値がない場合、空のコレクションが返されることを確認"""
        result = filter_by_value(sample_collection, "A", 100)

        # 結果の検証
        assert len(result.step) == 0
        assert len(result["A"]) == 0

    def test_invalid_column(self, sample_collection):
        """存在しない列名でKeyErrorが発生することを確認"""
        with pytest.raises(KeyError, match="列'不存在'が存在しません"):
            filter_by_value(sample_collection, "不存在", 1)


class TestFilterOutNone:
    """filter_out_none関数のテスト"""

    def test_filter_all_columns_any_mode(self, sample_collection):
        """デフォルトモード(any)ですべての列からNoneを含む行を除外する"""
        result = filter_out_none(sample_collection)

        # 結果の検証: 列Cに含まれるNoneが2行目と4行目にあるため、それらが除外される
        assert len(result.step) == 3
        # Indicesオブジェクトの値を直接比較する代わりに個々の要素を確認
        assert result.step.values == [1, 3, 5]
        assert [result["A"][i] for i in range(3)] == [1, 3, 5]
        assert [result["B"][i] for i in range(3)] == [10, 30, 50]
        assert [result["C"][i] for i in range(3)] == [100, 300, 500]

    def test_filter_specific_columns(self, sample_collection):
        """特定の列のみを対象にNoneを除外する"""
        # 列Cのみを対象にフィルタリング
        result = filter_out_none(sample_collection, columns=["C"])

        # 結果の検証: 列Cに含まれるNoneが2行目と4行目にあるため、それらが除外される
        assert len(result.step) == 3
        # Indicesオブジェクトの値を直接比較する代わりに個々の要素を確認
        assert result.step.values == [1, 3, 5]
        assert [result["C"][i] for i in range(3)] == [100, 300, 500]

    def test_filter_all_mode(self, sample_collection):
        """allモードでフィルタリング（すべての列がNoneの行のみを除外）"""
        # テスト用にデータを拡張
        extended_collection = ColumnCollection(
            step=[1, 2, 3, 4, 5, 6],
            columns={
                "A": Column("1", "Column A", "N", [1, 2, None, 4, 5, None]),
                "B": Column("2", "Column B", "kg", [10, None, None, 40, 50, None]),
                "C": Column("3", "Column C", "m", [100, None, 300, None, 500, None]),
            },
            metadata=sample_collection.metadata,
        )

        result = filter_out_none(extended_collection, mode="all")

        # 結果の検証: すべての列がNoneの行は6行目のみ
        assert len(result.step) == 5
        # Indicesオブジェクトの値を直接比較する代わりに個々の要素を確認
        assert result.step.values == [1, 2, 3, 4, 5]

    def test_invalid_column(self, sample_collection):
        """存在しない列名でKeyErrorが発生することを確認"""
        with pytest.raises(KeyError, match="列'不存在'が存在しません"):
            filter_out_none(sample_collection, columns=["A", "不存在"])

    def test_invalid_mode(self, sample_collection):
        """無効なモードでValueErrorが発生することを確認"""
        with pytest.raises(
            ValueError, match="モードは'any'または'all'のいずれかである必要があります"
        ):
            filter_out_none(sample_collection, mode="invalid")

    def test_metadata_preserved(self, sample_collection):
        """フィルタリング後もメタデータが保持されていることを確認"""
        result = filter_out_none(sample_collection)
        assert result.metadata == sample_collection.metadata


class TestRemoveConsecutiveDuplicatesAcross:
    """remove_consecutive_duplicates_across関数のテスト"""

    @pytest.fixture
    def duplicate_collection(self):
        """連続重複データを持つColumnCollectionフィクスチャ"""
        return ColumnCollection(
            step=[1, 2, 3, 4, 5, 6, 7, 8],
            columns={
                "A": Column(
                    "1", "Column A", "N", [1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0]
                ),
                "B": Column(
                    "2",
                    "Column B",
                    "kg",
                    [10.0, 20.0, 30.0, 30.0, 40.0, 50.0, 60.0, 60.0],
                ),
                "C": Column("3", "Column C", "m", [5, 5, 2, 2, 8, 8, 9, 10]),
            },
            metadata={"description": "Test Collection with Duplicates"},
        )

    def test_all_mode(self, duplicate_collection):
        """'all'モードで、すべての列で同じ値が続く行を削除する"""
        result = remove_consecutive_duplicates_across(
            duplicate_collection, columns=["A", "B", "C"], dup_type="all"
        )

        # 結果の検証: 連続して同じ値が全列にある場合のみ除外される
        # 'all'モードでは、いずれかの列で値が変化していれば行が保持される
        assert len(result) == 7
        # 保持されるインデックス: 0,1,2,4,5,6,7
        assert result.step.values == [1, 2, 3, 5, 6, 7, 8]
        assert [result["A"][i] for i in range(7)] == [1.0, 1.0, 2.0, 3.0, 3.0, 4.0, 4.0]
        assert [result["B"][i] for i in range(7)] == [
            10.0,
            20.0,
            30.0,
            40.0,
            50.0,
            60.0,
            60.0,
        ]
        assert [result["C"][i] for i in range(7)] == [5, 5, 2, 8, 8, 9, 10]

    def test_any_mode(self, duplicate_collection):
        """'any'モードで、一部の列でも値が変化する場合はその行を保持する"""
        result = remove_consecutive_duplicates_across(
            duplicate_collection, columns=["A", "B", "C"], dup_type="any"
        )

        # 結果の検証: いずれかの列で値が変化していれば行が保持される
        assert len(result) == 7
        # 保持されるインデックス: 0,1,2,4,5,6,7
        assert result.step.values == [1, 2, 3, 5, 6, 7, 8]
        assert [result["A"][i] for i in range(7)] == [1.0, 1.0, 2.0, 3.0, 3.0, 4.0, 4.0]
        assert [result["B"][i] for i in range(7)] == [
            10.0,
            20.0,
            30.0,
            40.0,
            50.0,
            60.0,
            60.0,
        ]
        assert [result["C"][i] for i in range(7)] == [5, 5, 2, 8, 8, 9, 10]

    def test_subset_columns(self, duplicate_collection):
        """一部の列のみを対象に重複除去を行う"""
        result = remove_consecutive_duplicates_across(
            duplicate_collection, columns=["A", "C"], dup_type="all"  # Bは除外
        )

        # 結果の検証: A列とC列のみを考慮して重複を除去
        assert len(result) == 5
        # 'all'モードでA列とC列を考慮すると、インデックス0,1,2,5,7が保持される
        assert result.step.values == [1, 3, 5, 7, 8]
        assert [result["A"][i] for i in range(5)] == [1.0, 2.0, 3.0, 4.0, 4.0]
        # B列は考慮されていないが、フィルタリングの結果として値は残る
        assert [result["B"][i] for i in range(5)] == [10.0, 30.0, 40.0, 60.0, 60.0]
        assert [result["C"][i] for i in range(5)] == [5, 2, 8, 9, 10]

    def test_invalid_dup_type(self, duplicate_collection):
        """無効なdup_typeでValueErrorが発生することを確認"""
        with pytest.raises(
            ValueError, match="dup_typeは'all'または'any'である必要があります"
        ):
            remove_consecutive_duplicates_across(
                duplicate_collection, columns=["A", "B"], dup_type="invalid"
            )

    def test_invalid_column(self, duplicate_collection):
        """存在しない列名でKeyErrorが発生することを確認"""
        with pytest.raises(KeyError, match="列'不存在'が存在しません"):
            remove_consecutive_duplicates_across(
                duplicate_collection, columns=["A", "不存在"]
            )

    def test_empty_collection(self):
        """空のコレクションに対して適用した場合、空のコレクションが返されることを確認"""
        empty_collection = ColumnCollection(
            step=[],
            columns={
                "A": Column("1", "Column A", "N", []),
                "B": Column("2", "Column B", "kg", []),
            },
            metadata={"description": "Empty Collection"},
        )

        result = remove_consecutive_duplicates_across(
            empty_collection, columns=["A", "B"]
        )

        assert len(result) == 0
        assert result.metadata == empty_collection.metadata

    def test_metadata_preserved(self, duplicate_collection):
        """重複除去後もメタデータが保持されていることを確認"""
        result = remove_consecutive_duplicates_across(
            duplicate_collection, columns=["A", "B"]
        )
        assert result.metadata == duplicate_collection.metadata


class TestRemoveOutliers:
    """remove_outliers 関数のテスト"""

    @pytest.fixture
    def outlier_collection(self):
        """異常値を含むデータセットのフィクスチャ"""
        return ColumnCollection(
            step=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            columns={
                "Data": Column(
                    "1",
                    "Test Data",
                    "N",
                    # インデックス3と8に異常値（外れ値）を配置
                    [10.0, 10.2, 9.8, 50.0, 10.1, 10.3, 9.9, 10.2, -30.0, 10.1],
                ),
                "Category": Column(
                    "2",
                    "Category",
                    "",
                    ["A", "A", "A", "A", "B", "B", "B", "B", "B", "C"],
                ),
            },
            metadata={"description": "Test Collection with Outliers"},
        )

    def test_basic_outlier_removal(self, outlier_collection):
        """基本的な異常値の検出と除去をテスト"""
        result = remove_outliers(
            outlier_collection,
            column="Data",
            window_size=3,
            threshold=0.3,
            edge_handling="asymmetric",
        )

        # 結果の検証: 異常値が除外されていることを確認
        # 関数の実装に依存せず、結果が少なくとも元より少ないことと、極端な異常値が除外されていることを検証
        assert len(result) < len(outlier_collection)
        assert 50.0 not in result["Data"].values
        assert -30.0 not in result["Data"].values

    def test_with_different_parameters(self, outlier_collection):
        """異なるパラメータでの異常値除去をテスト"""
        # しきい値を高くして、より極端な異常値だけを除去
        result = remove_outliers(
            outlier_collection,
            column="Data",
            window_size=5,
            threshold=0.8,  # より高いしきい値
            edge_handling="symmetric",
        )

        # しきい値が高いので、本当に極端な異常値だけが除外されるはず
        # この場合、インデックス3の50.0とインデックス8の-30.0のみが除外される
        assert len(result) < len(outlier_collection)
        assert "Data" in result.columns
        assert -30.0 not in result["Data"].values
        assert 50.0 not in result["Data"].values

    def test_with_minimal_threshold(self, outlier_collection):
        """しきい値を非常に低くして、ほとんどのデータポイントが異常値と判定されるケース"""
        result = remove_outliers(
            outlier_collection,
            column="Data",
            threshold=0.01,  # 非常に低いしきい値
        )

        # しきい値が非常に低いため、多くのデータポイントが異常値と判定される
        # 正確な結果は移動平均の実装に依存するため、少なくとも異常値は除外されていることを確認
        assert len(result) < len(outlier_collection)
        assert -30.0 not in result["Data"].values
        assert 50.0 not in result["Data"].values

    def test_second_column_preserved(self, outlier_collection):
        """異常値除去時に他の列が適切に処理されることを確認"""
        result = remove_outliers(
            outlier_collection,
            column="Data",
            threshold=0.3,
        )

        # 他の列（Category）も適切にフィルタリングされていることを確認
        assert "Category" in result.columns
        # 少なくとも異常値の行が除外され、残りの行数と列数が一致することを確認
        assert len(result["Category"]) == len(result["Data"])
        assert len(result.step) == len(result["Data"])

    def test_metadata_preserved(self, outlier_collection):
        """メタデータが保持されていることを確認"""
        result = remove_outliers(
            outlier_collection,
            column="Data",
        )
        assert result.metadata == outlier_collection.metadata

    def test_invalid_column(self, outlier_collection):
        """存在しない列でKeyErrorが発生することを確認"""
        with pytest.raises(KeyError, match="列"):
            remove_outliers(outlier_collection, column="不存在")

    def test_method_chain(self, outlier_collection):
        """メソッドチェーンでの使用を確認"""
        from src.tascpy.operations.core.stats import moving_average

        # メソッドチェーンで異常値除去と移動平均を組み合わせる
        result = (
            outlier_collection.ops.remove_outliers(column="Data", threshold=0.3)
            .moving_average(column="Data", window_size=3, result_column="SmoothData")
            .end()
        )

        # 結果の検証
        assert "SmoothData" in result.columns
        assert len(result) < len(outlier_collection)  # 異常値が除去されている
        # 移動平均が計算されていることを確認
        assert any(
            result["SmoothData"][i] != result["Data"][i] for i in range(len(result))
        )
