import pytest
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn, StringColumn

class TestInterpolateBasic:
    """基本的内挿機能の構造テスト"""

    @pytest.fixture
    def simple_collection(self):
        steps = [1.0, 3.0, 5.0]
        data = {
            "temp": NumberColumn(None, "temp", "°C", [20.0, 40.0, 60.0]),
            "pressure": NumberColumn(None, "pressure", "MPa", [1.0, 2.0, 3.0]),
            "status": StringColumn(None, "status", "", ["low", "medium", "high"]),
        }
        return ColumnCollection(steps, data)

    def test_interpolate_with_point_count(self, simple_collection):
        result = simple_collection.ops.interpolate(point_count=5).end()
        assert len(result) == 5
        assert isinstance(result, ColumnCollection)
        assert "temp" in result.columns
        assert "status" in result.columns

    def test_interpolate_with_x_values(self, simple_collection):
        result = simple_collection.ops.interpolate(x_values=[1.0, 2.0, 4.0, 5.0]).end()
        assert len(result) == 4
        assert "pressure" in result.columns

    def test_exclusive_parameters(self, simple_collection):
        with pytest.raises(ValueError):
            simple_collection.ops.interpolate()
        with pytest.raises(ValueError):
            simple_collection.ops.interpolate(x_values=[1, 2], point_count=5)


class TestInterpolateColumnBased:
    """列名に基づく内挿の構造テスト"""

    @pytest.fixture
    def multi_column_collection(self):
        steps = [1.0, 2.0, 3.0, 4.0, 5.0]
        data = {
            "time": NumberColumn(None, "time", "s", [0.0, 0.5, 1.0, 1.5, 2.0]),
            "position": NumberColumn(None, "position", "mm", [0.0, 10.0, 20.0, 30.0, 40.0]),
            "velocity": NumberColumn(None, "velocity", "mm/s", [0.0, 20.0, 20.0, 20.0, 20.0]),
            "status": StringColumn(None, "status", "", ["start", "moving", "moving", "moving", "end"]),
        }
        return ColumnCollection(steps, data)

    def test_interpolate_by_column(self, multi_column_collection):
        result = multi_column_collection.ops.interpolate(
            base_column_name="position", x_values=[5.0, 15.0, 25.0, 35.0]
        ).end()
        assert len(result) == 4
        assert "time" in result.columns

    def test_columns_parameter(self, multi_column_collection):
        result = multi_column_collection.ops.interpolate(
            x_values=[1.5, 2.5, 3.5, 4.5],
            columns=["velocity"]
        ).end()
        assert "velocity" in result.columns

    def test_column_error_cases(self, multi_column_collection):
        with pytest.raises(KeyError):
            multi_column_collection.ops.interpolate(x_values=[1.5, 2.5], columns=["nonexistent"])
        with pytest.raises(KeyError):
            multi_column_collection.ops.interpolate(base_column_name="nonexistent", point_count=3)


class TestInterpolateEdgeCases:
    def test_empty_collection(self):
        empty_collection = ColumnCollection([], {})
        with pytest.raises(ValueError):
            empty_collection.ops.interpolate(point_count=5)

    def test_single_point_collection(self):
        single_point = ColumnCollection([1.0], {"value": NumberColumn(None, "value", "", [10.0])})
        result = single_point.ops.interpolate(point_count=1).end()
        assert len(result) == 1

    def test_out_of_range_interpolation(self):
        steps = [1.0, 3.0, 5.0]
        data = {
            "temp": NumberColumn(None, "temp", "°C", [20.0, 40.0, 60.0]),
            "status": StringColumn(None, "status", "", ["low", "medium", "high"]),
        }
        collection = ColumnCollection(steps, data)
        result = collection.ops.interpolate(x_values=[0.0, 6.0]).end()
        assert len(result) == 2


class TestInterpolateMetadata:
    @pytest.fixture
    def collection_with_metadata(self):
        steps = [1.0, 2.0, 3.0, 4.0, 5.0]
        data = {
            "temp": NumberColumn(None, "temp", "°C", [20.0, 30.0, 40.0, 50.0, 60.0]),
        }
        metadata = {
            "date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
            "source": "test_data"
        }
        return ColumnCollection(steps, data, metadata)
    
    def test_metadata_handling(self, collection_with_metadata):
        result = collection_with_metadata.ops.interpolate(x_values=[1.5, 2.5, 3.5]).end()
        assert "date" in result.metadata
        assert result.metadata["source"] == "test_data"
        assert result.metadata.get("interpolation_method") == "linear"
        assert result.metadata.get("interpolation_basis") == "step"