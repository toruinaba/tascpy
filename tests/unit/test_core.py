import pytest
from datetime import datetime, timedelta
import numpy as np

from src.tascpy.core.column import Column
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.step import Step
from src.tascpy.core.row import Row
from src.tascpy.operations.registry import operation, OperationRegistry
from src.tascpy.domains.factory import DomainCollectionFactory


@pytest.fixture
def basic_collection():
    """基本的なColumnCollectionのフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "A": Column("1", "A", "N", [1, 2, 3, 4, 5]),
            "B": Column("1", "B", "N", [5, 4, 3, 2, 1]),
        },
        metadata={"description": "Test collection"},
    )


class TestColumnCollection:
    """ColumnCollectionのテストクラス"""

    def test_initialization(self, basic_collection):
        """初期化テスト"""
        assert isinstance(basic_collection, ColumnCollection)
        assert len(basic_collection) == 5
        assert len(basic_collection.columns) == 2
        assert basic_collection.step.values == [1, 2, 3, 4, 5]
        assert basic_collection.metadata["description"] == "Test collection"

        a_col = basic_collection["A"]
        assert isinstance(a_col, Column)
        assert a_col.values == [1, 2, 3, 4, 5]

    def test_getitem(self, basic_collection):
        """getitemメソッドのテスト"""
        assert basic_collection["A"].values == [1, 2, 3, 4, 5]
        assert basic_collection[0].step == 1
        assert basic_collection[0].values == {"A": 1, "B": 5}
        assert isinstance(basic_collection[0], Row)
        assert isinstance(basic_collection[1:3], ColumnCollection)
        assert len(basic_collection[1:3]) == 2
        assert basic_collection[1:3].step.values == [2, 3]
        assert basic_collection[1:3]["A"].values == [2, 3]

    def test_clone(self, basic_collection):
        """cloneメソッドのテスト"""
        cloned = basic_collection.clone()
        assert cloned is not basic_collection
        assert cloned.step is not basic_collection.step
        assert cloned.columns["A"] is not basic_collection.columns["A"]
        assert cloned.metadata == basic_collection.metadata
        assert cloned["A"].values == basic_collection["A"].values

    def test_add_remove_column(self, basic_collection):
        """add_columnとremove_columnメソッドのテスト"""
        new_col = Column("3", "C", "N", [10, 20, 30, 40, 50])
        basic_collection.add_column("C", new_col)
        assert "C" in basic_collection.columns
        assert basic_collection["C"].values == [10, 20, 30, 40, 50]

        basic_collection.remove_column("C")
        assert "C" not in basic_collection.columns
        assert len(basic_collection.columns) == 2


class TestOperations:
    """操作のテストクラス"""

    @pytest.fixture(autouse=True)
    def setup_operations(self):
        """テスト用操作関数の登録"""

        @operation
        def test_filter(collection, column_name, value):
            """テスト用フィルタリング操作"""
            result = collection.clone()
            indices = [
                i
                for i, v in enumerate(collection.columns[column_name].values)
                if v == value
            ]

            new_step = Step(values=[collection.step.values[i] for i in indices])
            new_columns = {}
            for name, column in collection.columns.items():
                new_column = column.clone()
                new_column.values = [column.values[i] for i in indices]
                new_columns[name] = new_column

            return ColumnCollection(new_step, new_columns, collection.metadata.copy())

    def test_operation_registry(self, basic_collection):
        """操作レジストリのテスト"""
        registry = OperationRegistry.get_operations("core")
        assert "test_filter" in registry
        assert callable(registry["test_filter"])

        filter_func = registry["test_filter"]
        result = filter_func(basic_collection, "A", 3)

        assert isinstance(result, ColumnCollection)
        assert len(result) == 1
        assert result["A"].values == [3]
        assert result["B"].values == [3]

    def test_chain_methods(self, basic_collection):
        """メソッドチェーンのテスト"""
        result = basic_collection.ops.test_filter("A", 3).end()

        assert isinstance(result, ColumnCollection)
        assert len(result) == 1
        assert result["A"].values == [3]
        assert result["B"].values == [3]


class TestDomainConversion:
    """ドメイン変換のテストクラス"""

    @pytest.fixture
    def timeseries_domain(self):
        """時系列ドメインの準備"""

        class TimeSeriesCollection(ColumnCollection):
            def __init__(self, step=None, columns=None, metadata=None, frequency=None):
                super().__init__(step=step, columns=columns, metadata=metadata)
                if frequency is not None:
                    self.metadata["frequency"] = frequency

        def create_timeseries(**kwargs):
            return TimeSeriesCollection(**kwargs)

        DomainCollectionFactory.register("timeseries", create_timeseries)

        @operation(domain="timeseries")
        def resample(collection, new_frequency):
            """時系列データを指定された頻度でリサンプリング"""
            result = collection.clone()
            result.metadata["frequency"] = new_frequency
            result.metadata["resampled"] = True
            return result

    @pytest.fixture
    def basic_collection_for_domain(self):
        """ドメイン変換用のテストデータ"""
        return ColumnCollection(
            step=[1, 2, 3, 4, 5],
            columns={
                "values": Column(
                    "1", "values", "degree", [10.5, 20.5, 30.5, 40.5, 50.5]
                ),
                "flag": Column(
                    None, "flag", "boolean", [True, False, True, False, True]
                ),
            },
            metadata={"description": "Test time series collection"},
        )

    def test_domain_factory(self, timeseries_domain, basic_collection_for_domain):
        """ドメインファクトリのテスト"""
        timeseries = DomainCollectionFactory.create(
            "timeseries",
            step=[datetime(2023, 1, 1) + timedelta(days=i) for i in range(3)],
            columns={"temp": [20.1, 21.5, 19.8]},
            frequency="1D",
        )

        assert len(timeseries) == 3
        assert timeseries.metadata["frequency"] == "1D"

        # 既存コレクションからのドメイン変換
        converted = DomainCollectionFactory.from_collection(
            basic_collection_for_domain, domain="timeseries", frequency="1H"
        )

        assert len(converted) == 5
        assert converted.metadata["frequency"] == "1H"
        assert converted.metadata["description"] == "Test time series collection"
        assert converted.step.values == basic_collection_for_domain.step.values
        assert (
            converted["values"].values == basic_collection_for_domain["values"].values
        )
        assert converted["flag"].values == basic_collection_for_domain["flag"].values

    def test_as_domain_method(self, timeseries_domain, basic_collection_for_domain):
        """as_domainメソッドのテスト"""
        converted = basic_collection_for_domain.ops.as_domain(domain="timeseries")


# 統合テスト
def test_full_pipeline():
    """完全なパイプラインの統合テスト"""
    # 基本コレクションの作成
    collection = ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [1.0, 4.0, 9.0, 16.0, 25.0],
            "group": ["A", "A", "B", "B", "C"],
        },
    )

    # テスト用の操作を定義
    @operation
    def add_derived_column(collection, formula, output_column):
        """数式に基づいて派生列を追加"""
        result = collection.clone()

        # 単純な数式の評価（実際の実装ではより複雑に）
        if formula == "x^2":
            values = [x * x for x in collection.columns["x"].values]
        elif formula == "x+y":
            values = [
                x + y
                for x, y in zip(
                    collection.columns["x"].values, collection.columns["y"].values
                )
            ]
        else:
            values = [0] * len(collection)

        result.add_column(output_column, values)
        return result

    # 時系列ドメインを登録
    class TimeSeriesCollection(ColumnCollection):
        def __init__(self, step=None, columns=None, metadata=None, frequency=None):
            super().__init__(step=step, columns=columns, metadata=metadata)
            if frequency is not None:
                self.metadata["frequency"] = frequency

    def create_timeseries(**kwargs):
        return TimeSeriesCollection(**kwargs)

    DomainCollectionFactory.register("timeseries", create_timeseries)

    @operation(domain="timeseries")
    def moving_average(collection, column, window=3):
        """移動平均の計算"""
        result = collection.clone()
        values = collection.columns[column].values

        # 単純な移動平均の計算
        ma_values = []
        for i in range(len(values)):
            start = max(0, i - window // 2)
            end = min(len(values), i + window // 2 + 1)
            window_values = [v for v in values[start:end] if v is not None]

            if window_values:
                ma_values.append(sum(window_values) / len(window_values))
            else:
                ma_values.append(None)

        result.add_column(f"{column}_ma{window}", ma_values)
        return result

    # パイプラインの実行
    result = (
        collection.ops.add_derived_column("x+y", "sum")
        .filter_by_value("group", "A")
        .as_domain(domain="timeseries", start_date="2023-01-01", frequency="1D")
        .moving_average("sum", window=3)
        .end()
    )

    # 結果の検証
    assert len(result) == 2  # group="A"のデータのみ
    assert "sum" in result.columns
    assert "sum_ma3" in result.columns
    assert result.columns["sum"].values == [2.0, 6.0]  # x+y の結果
    assert isinstance(result.step.values[0], datetime)
