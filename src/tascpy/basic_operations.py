from .utils.operation_decorator import channel_operation
from .utils.data import filter_none_values, moving_average


@channel_operation(name="filter_none")
def filter_none(data):
    return filter_none_values(data)


@channel_operation(name="moving_average")
def moving_average(data, window_size=3, edge_handling="asymmetric"):
    return moving_average(data, window_size, edge_handling)
