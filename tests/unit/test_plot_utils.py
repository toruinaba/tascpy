import pytest
from unittest.mock import patch, MagicMock
from src.tascpy.utils.plot import plot_helper


class TestPlotUtils:
    def test_plot_helper_without_ax(self):
        """Test plot_helper without ax parameter"""
        with patch('src.tascpy.utils.plot.plt') as mock_plt:
            mock_fig = MagicMock()
            mock_plt.figure.return_value = mock_fig
            
            x_data = [1, 2, 3]
            y_data = [10, 20, 30]
            
            result = plot_helper(x_data, y_data)
            
            mock_plt.figure.assert_called_once()
            mock_plt.plot.assert_called_once_with(x_data, y_data)
            assert result == mock_fig

    def test_plot_helper_with_labels(self):
        """Test plot_helper with x_label and y_label"""
        with patch('src.tascpy.utils.plot.plt') as mock_plt:
            mock_fig = MagicMock()
            mock_plt.figure.return_value = mock_fig
            
            x_data = [1, 2, 3]
            y_data = [10, 20, 30]
            x_label = "X Axis"
            y_label = "Y Axis"
            
            result = plot_helper(x_data, y_data, x_label=x_label, y_label=y_label)
            
            mock_plt.figure.assert_called_once()
            mock_plt.plot.assert_called_once_with(x_data, y_data)
            mock_plt.xlabel.assert_called_once_with(x_label)
            mock_plt.ylabel.assert_called_once_with(y_label)
            assert result == mock_fig

    def test_plot_helper_with_ax(self):
        """Test plot_helper with ax parameter"""
        mock_ax = MagicMock()
        
        x_data = [1, 2, 3]
        y_data = [10, 20, 30]
        
        result = plot_helper(x_data, y_data, ax=mock_ax)
        
        mock_ax.plot.assert_called_once_with(x_data, y_data)
        assert result == mock_ax

    def test_plot_helper_with_ax_and_labels(self):
        """Test plot_helper with ax, x_label, and y_label"""
        mock_ax = MagicMock()
        
        x_data = [1, 2, 3]
        y_data = [10, 20, 30]
        x_label = "X Axis"
        y_label = "Y Axis"
        
        result = plot_helper(x_data, y_data, x_label=x_label, y_label=y_label, ax=mock_ax)
        
        mock_ax.plot.assert_called_once_with(x_data, y_data)
        mock_ax.set_xlabel.assert_called_once_with(x_label)
        mock_ax.set_ylabel.assert_called_once_with(y_label)
        assert result == mock_ax

    def test_plot_helper_with_kwargs(self):
        """Test plot_helper with additional kwargs"""
        mock_ax = MagicMock()
        
        x_data = [1, 2, 3]
        y_data = [10, 20, 30]
        kwargs = {"color": "red", "marker": "o", "linestyle": "--"}
        
        result = plot_helper(x_data, y_data, ax=mock_ax, **kwargs)
        
        mock_ax.plot.assert_called_once_with(x_data, y_data, **kwargs)
        assert result == mock_ax
