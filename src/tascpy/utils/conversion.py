from typing import Union


def to_str(self, value: Union[float, bool, None]) -> str:
    if isinstance(value, bool):
        return "*******"
    elif value is None:
        return "none"
    else:
        return str(value)


def opt_float(value: str, nan = None) -> Union[float, bool, None]:
    try:
        return float(value)
    except ValueError:
        if value == "none":
            return nan
        else:
            return False