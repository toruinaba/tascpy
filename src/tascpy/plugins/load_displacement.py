from typing import Union

def cycle_count(data: Union[float, bool, None], step=0.5):
    cycle = [1.0]
    for i in range(1, len(data)):
        if data[i] * data[i - 1] < 0:
            c = cycle[i - 1] + step
            cycle.append(c)
        else:
            cycle.append(cycle[i - 1])
    markers = [int(c) for c in cycle]
    return markers
