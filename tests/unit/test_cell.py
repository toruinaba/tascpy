import pytest
from src.tascpy.cell import Cell


class TestCell:
    def test_init(self):
        """Test Cell initialization"""
        cell = Cell(ch="CH1", name="Test", unit="kg", step=1, data=10.5)
        assert cell.ch == "CH1"
        assert cell.name == "Test"
        assert cell.unit == "kg"
        assert cell.step == 1
        assert cell.data == 10.5

    def test_init_with_bool(self):
        """Test Cell initialization with boolean data"""
        cell = Cell(ch="CH1", name="Test", unit="kg", step=1, data=False)
        assert cell.data is False

    def test_init_with_none(self):
        """Test Cell initialization with None data"""
        cell = Cell(ch="CH1", name="Test", unit="kg", step=1, data=None)
        assert cell.data is None

    def test_to_dict(self):
        """Test to_dict method"""
        cell = Cell(ch="CH1", name="Test", unit="kg", step=1, data=10.5)
        cell_dict = cell.to_dict()
        assert isinstance(cell_dict, dict)
        assert cell_dict["ch"] == "CH1"
        assert cell_dict["name"] == "Test"
        assert cell_dict["unit"] == "kg"
        assert cell_dict["step"] == 1
        assert cell_dict["data"] == 10.5
