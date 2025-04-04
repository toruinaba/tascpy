import pytest
from unittest.mock import patch, MagicMock
from src.tascpy.step import Step
from src.tascpy.cell import Cell


class TestStep:
    @pytest.fixture
    def sample_step(self):
        """Create a sample step for testing"""
        chs = ["CH1", "CH2", "CH3"]
        names = ["Test1", "Test2", "Test3"]
        units = ["kg", "m", "s"]
        step = 1
        row = [10.5, 20.3, None]
        return Step(chs, names, units, step, row)

    def test_init(self, sample_step):
        """Test Step initialization"""
        assert sample_step.chs == ["CH1", "CH2", "CH3"]
        assert sample_step.names == ["Test1", "Test2", "Test3"]
        assert len(sample_step.dict) == 3
        
        # Check if dict contains Cell objects
        for ch in ["CH1", "CH2", "CH3"]:
            assert isinstance(sample_step.dict[ch], Cell)
        
        # Check Cell values
        assert sample_step.dict["CH1"].data == 10.5
        assert sample_step.dict["CH2"].data == 20.3
        assert sample_step.dict["CH3"].data is None

    def test_getitem_by_ch(self, sample_step):
        """Test __getitem__ method with channel key"""
        cell = sample_step["CH1"]
        assert isinstance(cell, Cell)
        assert cell.ch == "CH1"
        assert cell.name == "Test1"
        assert cell.unit == "kg"
        assert cell.step == 1
        assert cell.data == 10.5

    def test_getitem_by_name(self, sample_step):
        """Test __getitem__ method with name key"""
        cell = sample_step["Test2"]
        assert isinstance(cell, Cell)
        assert cell.ch == "CH2"
        assert cell.name == "Test2"
        assert cell.unit == "m"
        assert cell.step == 1
        assert cell.data == 20.3

    def test_repr(self, sample_step):
        """Test __repr__ method"""
        assert str(sample_step.dict) in repr(sample_step)

    def test_plot_const_x_with_string_list(self):
        """Test plot_const_x with list of strings"""
        # Create a mock for plot_helper
        mock_plot_helper = MagicMock()
        mock_fig = MagicMock()
        mock_plot_helper.return_value = mock_fig
        
        # Patch plot_helper
        with patch('src.tascpy.step.plot_helper', mock_plot_helper):
            step = Step(
                ["CH1", "CH2", "CH3"],
                ["Test1", "Test2", "Test3"],
                ["kg", "m", "s"],
                1,
                [10.5, 20.3, 30.1]
            )
            
            x = [1, 2, 3]
            y = ["Test1", "Test2", "Test3"]
            
            result = step.plot_const_x(x, y)
            
            # Verify plot_helper was called with correct arguments
            mock_plot_helper.assert_called_once_with(x, [10.5, 20.3, 30.1], ax=None)
            assert result == mock_fig

    def test_plot_const_x_with_nested_list(self):
        """Test plot_const_x with nested list"""
        # Create a mock for plot_helper
        mock_plot_helper = MagicMock()
        mock_fig = MagicMock()
        mock_plot_helper.return_value = mock_fig
        
        # Patch plot_helper
        with patch('src.tascpy.step.plot_helper', mock_plot_helper):
            step = Step(
                ["CH1", "CH2", "CH3"],
                ["Test1", "Test2", "Test3"],
                ["kg", "m", "s"],
                1,
                [10.5, 20.3, 30.1]
            )
            
            x = [1, 2, 3]
            y = [["Test1", "Test2"], ["Test3"]]
            
            result = step.plot_const_x(x, y)
            
            # Verify plot_helper was called with correct arguments
            assert mock_plot_helper.call_count == 2
            mock_plot_helper.assert_any_call(x, [10.5, 20.3], ax=None)
            mock_plot_helper.assert_any_call(x, [30.1], ax=None)
            assert result == mock_fig

    def test_plot_const_x_with_ax(self):
        """Test plot_const_x with ax parameter"""
        mock_ax = MagicMock()
        
        step = Step(
            ["CH1", "CH2", "CH3"],
            ["Test1", "Test2", "Test3"],
            ["kg", "m", "s"],
            1,
            [10.5, 20.3, 30.1]
        )
        
        x = [1, 2, 3]
        y = ["Test1", "Test2", "Test3"]
        
        result = step.plot_const_x(x, y, ax=mock_ax)
        
        mock_ax.plot.assert_called_once_with(x, [10.5, 20.3, 30.1])
        assert result == mock_ax

    def test_plot_const_y_with_string_list(self):
        """Test plot_const_y with list of strings"""
        # Create a mock for plot_helper
        mock_plot_helper = MagicMock()
        mock_fig = MagicMock()
        mock_plot_helper.return_value = mock_fig
        
        # Patch plot_helper
        with patch('src.tascpy.step.plot_helper', mock_plot_helper):
            step = Step(
                ["CH1", "CH2", "CH3"],
                ["Test1", "Test2", "Test3"],
                ["kg", "m", "s"],
                1,
                [10.5, 20.3, 30.1]
            )
            
            y = [1, 2, 3]
            x = ["Test1", "Test2", "Test3"]
            
            result = step.plot_const_y(y, x)
            
            # Verify plot_helper was called with correct arguments
            mock_plot_helper.assert_called_once_with([10.5, 20.3, 30.1], y, ax=None)
            assert result == mock_fig

    def test_plot_const_y_with_nested_list(self):
        """Test plot_const_y with nested list"""
        # Create a mock for plot_helper
        mock_plot_helper = MagicMock()
        mock_fig = MagicMock()
        mock_plot_helper.return_value = mock_fig
        
        # Patch plot_helper
        with patch('src.tascpy.step.plot_helper', mock_plot_helper):
            step = Step(
                ["CH1", "CH2", "CH3"],
                ["Test1", "Test2", "Test3"],
                ["kg", "m", "s"],
                1,
                [10.5, 20.3, 30.1]
            )
            
            y = [1, 2, 3]
            x = [["Test1", "Test2"], ["Test3"]]
            
            result = step.plot_const_y(y, x)
            
            # Verify plot_helper was called with correct arguments
            assert mock_plot_helper.call_count == 2
            mock_plot_helper.assert_any_call([10.5, 20.3], y, ax=None)
            mock_plot_helper.assert_any_call([30.1], y, ax=None)
            assert result == mock_fig

    def test_plot_const_y_with_ax(self):
        """Test plot_const_y with ax parameter"""
        mock_ax = MagicMock()
        
        step = Step(
            ["CH1", "CH2", "CH3"],
            ["Test1", "Test2", "Test3"],
            ["kg", "m", "s"],
            1,
            [10.5, 20.3, 30.1]
        )
        
        y = [1, 2, 3]
        x = ["Test1", "Test2", "Test3"]
        
        result = step.plot_const_y(y, x, ax=mock_ax)
        
        mock_ax.plot.assert_called_once_with([10.5, 20.3, 30.1], y)
        assert result == mock_ax

    def test_to_dict(self, sample_step):
        """Test to_dict method"""
        step_dict = sample_step.to_dict()
        assert isinstance(step_dict, dict)
        assert "CH1" in step_dict
        assert "CH2" in step_dict
        assert "CH3" in step_dict
        
        # Check if each value is a dictionary from Cell.to_dict()
        for ch in ["CH1", "CH2", "CH3"]:
            assert isinstance(step_dict[ch], dict)
            assert "ch" in step_dict[ch]
            assert "name" in step_dict[ch]
            assert "unit" in step_dict[ch]
            assert "step" in step_dict[ch]
            assert "data" in step_dict[ch]
