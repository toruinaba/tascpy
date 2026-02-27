
import pytest
import numpy as np
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.core.column import Column
from tascpy.operations.load_displacement.analysis import (
    calculate_slopes,
    calculate_stiffness,
    find_yield_point,
)

@pytest.fixture
def linear_collection():
    """Create a simple linear load-displacement collection"""
    # y = 2x
    x = np.linspace(0, 10, 101)
    y = 2 * x
    
    col_x = Column(ch=None, name="displacement", unit="mm", values=x)
    col_y = Column(ch=None, name="load", unit="kN", values=y)
    
    c = LoadDisplacementCollection(
        step=list(range(101)), 
        columns={"displacement": col_x, "load": col_y}
    )
    return c

@pytest.fixture
def bilinear_collection():
    """Create a bilinear load-displacement collection (elastic-plastic)"""
    # Elastic: y = 10x for x in [0, 5] -> y in [0, 50]
    # Plastic: y = 50 + 1*(x-5) for x in [5, 10] -> y in [50, 55]
    
    x1 = np.linspace(0, 5, 51)
    y1 = 10 * x1
    
    x2 = np.linspace(5.1, 10, 50) # Avoid duplicate 5.0
    y2 = 50 + 1 * (x2 - 5)
    
    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    
    col_x = Column(ch=None, name="displacement", unit="mm", values=x)
    col_y = Column(ch=None, name="load", unit="kN", values=y)
    
    c = LoadDisplacementCollection(
        step=list(range(len(x))), 
        columns={"displacement": col_x, "load": col_y}
    )
    return c

class TestCalculateSlopes:
    def test_basic_slopes(self, linear_collection):
        # y = 2x, slope should be 2 everywhere
        res = calculate_slopes(linear_collection)
        
        slope_col_name = "slope_data"
        assert slope_col_name in res.columns
        slopes = res.columns[slope_col_name].values
        
        # First point is NaN
        assert np.isnan(slopes[0])
        # Others are 2.0
        np.testing.assert_allclose(slopes[1:], 2.0)

    def test_insufficient_data(self):
        c = LoadDisplacementCollection(
            step=[0], 
            columns={
                "displacement": Column(ch=None, name="displacement", unit="mm", values=[0.0]),
                "load": Column(ch=None, name="load", unit="kN", values=[0.0])
            }
        )
        with pytest.raises(ValueError, match="2つ以上のデータポイントが必要です"):
            calculate_slopes(c)

class TestCalculateStiffness:
    def test_linear_regression(self, linear_collection):
        # stiffness = 2.0
        # range_start=0.2, range_end=0.8
        # max load = 20. range 4 to 16.
        val = calculate_stiffness(linear_collection, method="linear_regression")
        assert val == pytest.approx(2.0)

    def test_secant(self, linear_collection):
        val = calculate_stiffness(linear_collection, method="secant")
        assert val == pytest.approx(2.0)

    def test_insufficient_range_data(self, linear_collection):
        # linear_collection has 101 points (0..10). max load 20.
        # y steps are 0.2.
        # Use range that falls between steps.
        # 5.0 to 5.2 are existing points.
        # Try range 5.05 to 5.15 -> no points.
        # 5.05 / 20 = 0.2525
        # 5.15 / 20 = 0.2575
        with pytest.raises(ValueError, match="十分なデータがありません"):
            calculate_stiffness(linear_collection, range_start=0.2525, range_end=0.2575)

class TestFindYieldPoint:
    def test_offset_method_success(self, bilinear_collection):
        # Elastic slope = 10.
        # Plastic slope = 1.
        # Offset 0.2% (0.002).
        # We need to adjust parameters to make sure it finds it.
        # default range_start=0.1, range_end=0.3.
        # max_load = 55.
        # range 5.5 to 16.5.
        # In this range (elastic), slope is 10.
        # Offset line: y = 10(x - offset_val*max_disp?) No, logic is:
        # offset_amount = initial_slope * offset_value
        # offset_line = initial_slope * disp_data - offset_amount
        # = 10 * x - 10 * 0.002
        # = 10x - 0.02.
        # This is parallel to elastic line (y=10x) but shifted down/right.
        # It will intersect where plastic line (y=50 + x - 5) meets it?
        # Actually standard offset method shifts x by e.g. 0.2% strain.
        # Here offset_value seems to be absolute x shift if unit is consistent?
        # Code: offset_amount = initial_slope * offset_value. offset_line = slope*x - offset_amount.
        # y = m(x - offset_value). Yes.
        # So offset_value is an X-axis shift.
        # If I use offset_value=1.0. Line y = 10(x-1).
        # Intersection with plastic line y = x + 45.
        # 10x - 10 = x + 45 -> 9x = 55 -> x = 6.11.
        
        res = find_yield_point(
            bilinear_collection, 
            method="offset", 
            offset_value=1.0, 
        )
        
        # Check result metadata status
        assert "yield_point" in res.results
        yp = res.results["yield_point"]
        assert yp.metadata["is_valid"] is True
        
        # Check values
        yp_disp = yp.x
        yp_load = yp.y
        
        assert yp_disp == pytest.approx(6.11, abs=0.1)
        # y = 10(6.11 - 1) = 51.1
        assert yp_load == pytest.approx(51.1, abs=1.0)

    def test_offset_method_fail_silently(self, linear_collection):
        # Linear data never intersects with offset line (parallel)
        # y = 2x. Offset y = 2(x - 1) = 2x - 2.
        # Parallel, no intersection.
        
        res = find_yield_point(
            linear_collection,
            method="offset",
            offset_value=1.0,
            fail_silently=True,
        )
        
        assert "yield_point" in res.results
        yp = res.results["yield_point"]
        assert yp.metadata["is_valid"] is False
        assert np.isnan(yp.x)
        assert np.isnan(yp.y)

    def test_offset_method_fail_raise(self, linear_collection):
        # By default it doesn't raise exception for no intersection, it just sets is_valid=False
        res = find_yield_point(
            linear_collection,
            method="offset",
            offset_value=1.0,
        )
        assert res.results["yield_point"].metadata["is_valid"] is False

    def test_general_method_success(self, bilinear_collection):
        # General method: point where slope becomes factor * initial_slope
        # Initial slope = 10.
        # Plastic slope = 1.
        # Factor = 0.5 -> Threshold = 5.
        # Slope becomes 1 (which is < 5) at plastic region (index 6, x=6).
        
        res = find_yield_point(
            bilinear_collection,
            method="general",
            factor=0.5,
        )
        
        assert "yield_point" in res.results
        yp = res.results["yield_point"]
        assert yp.metadata["is_valid"] is True
        
        yp_disp = yp.x
        assert yp_disp == pytest.approx(6.0, abs=1.0)


    def test_verify_debug_info(self, bilinear_collection):
        res = find_yield_point(
            bilinear_collection,
            method="offset",
            offset_value=1.0,
            debug_mode=True
        )
        debug_info = res.results["yield_point"].metadata
        assert "initial_slope" in debug_info
        assert "diff_stats" in debug_info
