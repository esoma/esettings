__all__ = ["convert_value_to_type", "TypeConversionError"]

from types import NoneType
from types import UnionType
from typing import Callable
from typing import Final
from typing import Mapping
from typing import Union
from typing import get_args as get_typing_args
from typing import get_origin as get_typing_origin

from ._schema import PlainSchemaType
from ._schema import Schema
from ._schema import SchemaType


class TypeConversionError(RuntimeError):
    pass


def _convert_value_to_int(raw_value: str, type: type[SchemaType]) -> int:
    try:
        return int(raw_value)
    except ValueError:
        raise TypeConversionError()


def _convert_value_to_float(raw_value: str, type: type[SchemaType]) -> float:
    try:
        return float(raw_value)
    except ValueError:
        raise TypeConversionError()


def _convert_value_to_str(raw_value: str, type: type[SchemaType]) -> str:
    return raw_value


def _convert_value_to_none(raw_value: str, type: type[SchemaType]) -> None:
    if raw_value == "":
        return None
    raise TypeConversionError()


def _convert_value_to_bool(raw_value: str, type: type[SchemaType]) -> bool:
    if raw_value == "true":
        return True
    if raw_value == "false":
        return False
    raise TypeConversionError()


def _convert_value_to_list(raw_value: str, type: type[SchemaType]) -> list[PlainSchemaType]:
    try:
        typing_arg = get_typing_args(type)[0]
    except IndexError:
        raise RuntimeError(f"schema type: {type!r} is missing item type specifier")
    if get_typing_origin(typing_arg) in (Union, UnionType):
        sub_types = get_typing_args(typing_arg)
    else:
        sub_types = (typing_arg,)

    values: list[PlainSchemaType] = []
    for raw_value in raw_value.split(","):
        for sub_type in sub_types:
            try:
                value = convert_value_to_type(raw_value, sub_type)
            except TypeConversionError:
                continue
            assert not isinstance(value, list)
            values.append(value)
            break
        else:
            raise TypeConversionError()
    return values


_CONVERT_VALUE_TO_TYPE: Final[
    Mapping[type[SchemaType], Callable[[str, type[SchemaType]], SchemaType]]
] = {
    NoneType: _convert_value_to_none,
    str: _convert_value_to_str,
    int: _convert_value_to_int,
    float: _convert_value_to_float,
    bool: _convert_value_to_bool,
    list: _convert_value_to_list,
}


def convert_value_to_type(raw_value: str, type: type[SchemaType]) -> SchemaType:
    base_type = get_typing_origin(type)
    if base_type is None:
        base_type = type
    if base_type is None:
        base_type = NoneType

    try:
        convert_value_to_type = _CONVERT_VALUE_TO_TYPE[base_type]
    except KeyError:
        raise RuntimeError(f"unexpected schema type: {type!r}")
    return convert_value_to_type(raw_value, type)
