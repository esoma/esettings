__all__ = ["convert_string"]

from typing import Any

from tomllib import TOMLDecodeError
from tomllib import loads as toml_loads


def convert_string(raw_value: str) -> Any:
    try:
        result = toml_loads(f"value = {raw_value}")
    except TOMLDecodeError:
        raise ValueError()
    if set(result.keys()) != {"value"}:
        raise ValueError()
    return result["value"]
