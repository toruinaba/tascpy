import pytest
import numpy as np
from tascpy.core.step import Step

def test_step_find_step_index():
    step = Step([1.0, 2.0, 3.0, 4.0, 5.0])
    
    # Exact match
    assert step.find_step_index(3.0) == 2
    
    # Not found default
    assert step.find_step_index(10.0, default=-1) == -1
    
    # With tolerance
    assert step.find_step_index(3.01, tolerance=0.05) == 2
    assert step.find_step_index(10.0, tolerance=0.1, default=-1) == -1

    # Empty
    empty_step = Step([])
    assert empty_step.find_step_index(1.0, default=-1) == -1

def test_step_find_nearest_index():
    step = Step([1.0, 2.0, 3.5, 4.0, 5.0])
    
    # Nearest
    assert step.find_nearest_index(3.4) == 2
    assert step.find_nearest_index(3.7) == 2  # wait, 3.7 nearest to 3.5 is dist 0.2, 4.0 is dist 0.3, so 2
    assert step.find_nearest_index(6.0) == 4
    
    # Empty
    empty_step = Step([])
    assert empty_step.find_nearest_index(1.0) == -1

    # Non-numeric array
    str_step = Step(["a", "b", "c"])
    with pytest.raises(TypeError):
        str_step.find_nearest_index("b")
