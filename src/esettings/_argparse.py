__all__ = ["ARGUMENT_NOT_SUPPLIED", "build_argument_parser", "load_settings_from_argument_parser"]

from argparse import ArgumentParser
from argparse import Namespace
from itertools import islice
from re import sub as re_sub
from typing import Callable
from typing import Final
from typing import Mapping

from ._convert import TypeConversionError
from ._convert import convert_value_to_type
from ._schema import Schema
from ._settings import Settings

ARGUMENT_NOT_SUPPLIED: Final = object()


def build_argument_parser(
    argument_parser: ArgumentParser, schema: Schema, *, help: Mapping[tuple[str, ...], str] = {}
) -> None:
    for name, types in schema.items():
        argument_parser.add_argument(
            _build_arg_name(*name),
            default=ARGUMENT_NOT_SUPPLIED,
            const="",
            nargs="?",
            help=help.get(name),
            metavar="",
        )


def load_settings_from_argument_parser(
    namespace: Namespace,
    schema: Schema,
    *,
    on_failure: Callable[[tuple[str, ...], str], None] = lambda n, v: None,
) -> Settings:
    settings: Settings = {}

    for name, types in schema.items():
        # get the value from the namespace
        raw_value = getattr(namespace, _build_arg_dest(*name))
        if raw_value is ARGUMENT_NOT_SUPPLIED:
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


def _build_arg_name(*name: str) -> str:
    return "--" + "-".join(_convert_name_component_to_arg_name(c) for c in name)


def _build_arg_dest(*name: str) -> str:
    return _build_arg_name(*name).replace("-", "_")[2:]


def _convert_name_component_to_arg_name(component: str) -> str:
    return re_sub(r"[_\s]+", "-", component).lower()
