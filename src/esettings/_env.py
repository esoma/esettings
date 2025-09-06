__all__ = ["load_settings_from_environment", "get_environment_variables_from_schema"]

from itertools import islice
from os import environ
from re import sub as re_sub
from types import NoneType
from types import UnionType
from typing import Callable
from typing import Final
from typing import Mapping
from typing import Sequence
from typing import Union
from typing import get_args as get_typing_args
from typing import get_origin as get_typing_origin

from ._schema import PlainSchemaType
from ._schema import Schema
from ._schema import SchemaType
from ._settings import Settings


def get_environment_variables_from_schema(
    schema: Schema, *, prefix: str | None = None
) -> dict[tuple[str, ...], str]:
    prefixes: tuple[str, ...] = ()
    if prefix is not None:
        prefixes = (prefix,)

    return {name: _build_env_key(*prefixes, *name) for name in schema}


def load_settings_from_environment(
    schema: Schema,
    *,
    prefix: str | None = None,
    on_failure: Callable[[tuple[str, ...], str], None] = lambda n, v: None,
) -> Settings:
    settings: Settings = {}

    environment_variables = get_environment_variables_from_schema(schema, prefix=prefix)

    for name, types in schema.items():
        # get the value from the environment
        env_var = environment_variables[name]
        try:
            raw_value = environ[env_var]
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
            on_failure(name, raw_value)
            continue
        # store in the correct place
        target = settings
        for component in islice(name, len(name) - 1):
            try:
                target = settings[component]
                assert isinstance(target, dict)
            except KeyError:
                target = settings[component] = {}
        target[name[-1]] = value

    return settings


def _build_env_key(*name: str) -> str:
    return "_".join(_convert_name_component_to_env_key(c) for c in name)


def _convert_name_component_to_env_key(component: str) -> str:
    return re_sub(r"[\-\s]+", "_", component).upper()


class _TypeConversionError(RuntimeError):
    pass


def _convert_value_to_int(raw_value: str, type: type[SchemaType]) -> int:
    try:
        return int(raw_value)
    except ValueError:
        raise _TypeConversionError()


def _convert_value_to_float(raw_value: str, type: type[SchemaType]) -> float:
    try:
        return float(raw_value)
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
                value = _convert_value_to_type(raw_value, sub_type)
            except _TypeConversionError:
                continue
            assert not isinstance(value, list)
            values.append(value)
            break
        else:
            raise _TypeConversionError()
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


def _convert_value_to_type(raw_value: str, type: type[SchemaType]) -> SchemaType:
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
