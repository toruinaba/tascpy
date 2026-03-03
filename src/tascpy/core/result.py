from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, List
from .column import Column

class AnalysisResult(ABC):
    """Base class for any analysis result separate from the main data columns."""
    
    def __init__(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.metadata = metadata or {}

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization/API response."""
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}'>"


class XYSeriesResult(AnalysisResult):
    """Represents a generic 2D series (curve) with X and Y columns.
    
    Examples:
        >>> from tascpy.core.result import XYSeriesResult
        >>> from tascpy.core.column import NumberColumn
        >>> x = NumberColumn("X", "X-Axis", "mm", [0, 1])
        >>> y = NumberColumn("Y", "Y-Axis", "N", [0, 10])
        >>> res = XYSeriesResult("Curve", x, y)
        >>> res.x.name
        'X-Axis'
    """
    
    def __init__(
        self, 
        name: str, 
        x: Column, 
        y: Column, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name, metadata)
        self.x = x
        self.y = y

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "xy_series",
            "name": self.name,
            "data": {
                "x": self.x.values, 
                "y": self.y.values
            },
            "columns": {
                "x": self.x,
                "y": self.y
            },
            "metadata": self.metadata
        }
    
    def to_csv(self, path: str, encoding: str = "utf-8", include_header: bool = True) -> None:
        """Export series data to CSV file."""
        import csv
        
        with open(path, mode="w", encoding=encoding, newline="") as f:
            writer = csv.writer(f)
            if include_header:
                writer.writerow(["x", "y"])
            
            x_vals = self.x.values
            y_vals = self.y.values
            
            for i in range(max(len(x_vals), len(y_vals))):
                x = x_vals[i] if i < len(x_vals) else None
                y = y_vals[i] if i < len(y_vals) else None
                writer.writerow([x, y])

# Alias for backward compatibility or clarity if needed, though we will use XYSeriesResult primarily
Curve = XYSeriesResult


class ScalarResult(AnalysisResult):
    """Represents a single scalar result (e.g. Stiffness, Max Load).
    
    Examples:
        >>> from tascpy.core.result import ScalarResult
        >>> res = ScalarResult("MaxLoad", 100.0, "N")
        >>> res.value
        100.0
    """
    
    def __init__(
        self, 
        name: str, 
        value: Any, 
        unit: Optional[str] = None, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name, metadata)
        self.value = value
        self.unit = unit

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "scalar", 
            "name": self.name, 
            "value": self.value, 
            "unit": self.unit, 
            "metadata": self.metadata
        }
    
    def __repr__(self) -> str:
        val_str = f"{self.value}"
        if self.unit:
            val_str += f" {self.unit}"
        return f"<{self.__class__.__name__} name='{self.name}' value={val_str}>"


class PointResult(AnalysisResult):
    """Represents a specific point (x, y) with optional units.
    
    Examples:
        >>> from tascpy.core.result import PointResult
        >>> res = PointResult("YieldPoint", 1.0, 10.0, "mm", "kN")
        >>> res.y
        10.0
    """
    
    def __init__(
        self, 
        name: str, 
        x: float, 
        y: float, 
        x_unit: Optional[str] = None, 
        y_unit: Optional[str] = None, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name, metadata)
        self.x = x
        self.y = y
        self.x_unit = x_unit
        self.y_unit = y_unit
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "point",
            "name": self.name,
            "data": {"x": self.x, "y": self.y},
            "units": {"x": self.x_unit, "y": self.y_unit},
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' x={self.x} y={self.y}>"
