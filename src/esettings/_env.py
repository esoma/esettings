__all__ = []

from itertools import islice
from os import environ
from re import sub as re_sub
from types import UnionType
from typing import Callable
from typing import Final
from typing import Mapping
from typing import Sequence
from typing import Union
from typing import get_args as get_typing_args
from typing import get_origin as get_typing_origin

from ._schema import Schema
from ._schema import SchemaType
from ._settings import Settings


def load_settings_from_environment(schema: Schema, *, prefix: str | None = None) -> Settings:
    settings: Settings = {}

    prefixes: tuple[str, ...] = ()
    if prefix is not None:
        prefixes = (prefix,)

    for name, types in schema.items():
        # get the value from the environment
        env_key = _build_env_key(*prefixes, *name)
        try:
            raw_value = environ[env_key]
        except KeyError:
            continue
        # convert to the correct type
        for type in types:
            try:
                value = _convert_value_to_type(raw_value, type)
            except _TypeConversionError:
                continue
            break
        else:
            continue
        # store in the correct place
        target = settings
        for component in islice(name, len(name) - 1):
            try:
                target = settings[component]
            except KeyError:
                target = settings[component] = {}
        target[name[-1]] = value

    return settings


def _build_env_key(*name: str) -> str:
    return "_".join(_sanitize_env_component(c) for c in name)


def _sanitize_env_component(component: str) -> str:
    key = re_sub(r"[^a-zA-Z0-9\-_\s]", "", component)
    key = re_sub(r"[\-\s]+", "_", key)
    return key.strip("_").upper()


class _TypeConversionError(RuntimeError):
    pass


def _convert_value_to_int(raw_value: str, type: type[SchemaType]) -> int:
    try:
        return int(raw_value)
    except ValueError:
        raise _TypeConversionError()


def _convert_value_to_str(raw_value: str, type: type[SchemaType]) -> str:
    return raw_value


def _convert_value_to_none(raw_value: str, type: type[SchemaType]) -> None:
    if raw_value == "":
        return None
    raise _TypeConversionError()


def _convert_value_to_bool(raw_value: str, type: type[SchemaType]) -> bool:
    if raw_value == "true":
        return True
    if raw_value == "false":
        return False
    raise _TypeConversionError()


def _convert_value_to_list(raw_value: str, type: type[SchemaType]) -> list[SchemaType]:
    try:
        typing_arg = get_typing_args(type)[0]
    except IndexError:
        raise RuntimeError(f"schema type: {type!r} is missing item type specifier")
    if get_typing_origin(typing_arg) in (Union, UnionType):
        sub_types = get_typing_args(typing_arg)
    else:
        sub_types = (typing_arg,)

    values: list[SchemaType] = []
    for raw_value in raw_value.split(","):
        for sub_type in sub_types:
            try:
                value = _convert_value_to_type(raw_value, sub_type)
            except _TypeConversionError:
                continue
            values.append(value)
            break
        else:
            raise _TypeConversionError()
    return values


_CONVERT_VALUE_TO_TYPE: Final[Mapping[type[SchemaType], Callable[[str], SchemaType]]] = {
    None: _convert_value_to_none,
    str: _convert_value_to_str,
    int: _convert_value_to_int,
    bool: _convert_value_to_bool,
    list: _convert_value_to_list,
}


def _convert_value_to_type(raw_value: str, type: type[SchemaType]) -> SchemaType:
    base_type = get_typing_origin(type)
    if base_type is None:
        base_type = type
    try:
        convert_value_to_type = _CONVERT_VALUE_TO_TYPE[base_type]
    except KeyError:
        raise RuntimeError(f"unexpected schema type: {type!r}")
    return convert_value_to_type(raw_value, type)
