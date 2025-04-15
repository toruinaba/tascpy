from typing import Union

def cycle_count(data: Union[float, bool, None]):
    cycle = [1.0]
    for i in range(1, len(p)):
        if data[i] * data[i-1] < 0:
            c = cycle[i-1] + 0.5
            cycle.append(c)
        else:
            cycle.append(cycle[i-1])
    markers = [int(c) for c in cycle]
    return markers
