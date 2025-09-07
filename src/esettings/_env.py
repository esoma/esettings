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

from ._convert import TypeConversionError
from ._convert import convert_value_to_type
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
                value = convert_value_to_type(raw_value, type)
            except TypeConversionError:
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
