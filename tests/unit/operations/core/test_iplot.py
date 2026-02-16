
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from tascpy.operations.core.plot import iplot
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column

@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "x": Column("1", "X Values", "m", [1, 2, 3, 4, 5]),
            "y1": Column("2", "Y1 Values", "kg", [10, 20, 30, 40, 50]),
        },
        metadata={"description": "Test Collection for IPlot"},
    )

class TestIPlot:
    """iplot関数のテスト"""

    @patch("tascpy.visualization.backend_plotly.plot")
    def test_basic_iplot(self, mock_plotly_plot, sample_collection):
        """基本的なiplot呼び出しがbackend_plotly.plotに正しく委譲されることを確認"""
        # モックの戻り値設定
        mock_fig = MagicMock()
        mock_plotly_plot.return_value = mock_fig
        
        # iplot呼び出し
        result = iplot(sample_collection, "x", "y1")
        
        # 検証
        mock_plotly_plot.assert_called_once()
        args, kwargs = mock_plotly_plot.call_args
        
        # 引数の検証 (@inject_plot_dataが機能しているか)
        assert "x_values" in kwargs
        assert "y_values" in kwargs
        assert "x_label" in kwargs
        assert "y_label" in kwargs
        assert "title" in kwargs
        
        np.testing.assert_array_equal(kwargs["x_values"], sample_collection.columns["x"].values)
        np.testing.assert_array_equal(kwargs["y_values"], sample_collection.columns["y1"].values)
        assert kwargs["x_label"] == "X Values [m]"
        assert kwargs["y_label"] == "Y1 Values [kg]"
        assert kwargs["title"] == "Scatter plot of Y1 Values vs X Values"
        
        # 戻り値の検証
        assert result is mock_fig

    @patch("tascpy.visualization.backend_plotly.plot")
    def test_iplot_kwargs(self, mock_plotly_plot, sample_collection):
        """キーワード引数がbackend_plotly.plotに渡されることを確認"""
        iplot(sample_collection, "x", "y1", plot_type="line", color="red")
        
        args, kwargs = mock_plotly_plot.call_args
        assert kwargs.get("plot_type") == "line"
        assert kwargs.get("color") == "red"

    @patch("tascpy.visualization.backend_plotly.plot")
    def test_iplot_name_extraction(self, mock_plotly_plot, sample_collection):
        """name引数またはy_labelからnameが抽出されることを確認"""
        # 1. 自動抽出 (Y1 Values [kg] -> Y1 Values)
        iplot(sample_collection, "x", "y1")
        args, kwargs = mock_plotly_plot.call_args
        assert kwargs.get("name") == "Y1 Values"
        
        # 2. 明示的指定
        iplot(sample_collection, "x", "y1", name="Custom Name")
        args, kwargs = mock_plotly_plot.call_args
        assert kwargs.get("name") == "Custom Name"
