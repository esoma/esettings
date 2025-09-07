__all__ = ["load_from_environ"]

import os
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
from ._convert import convert_string
from ._convert import convert_value_to_type
from ._schema import PlainSchemaType
from ._schema import Schema
from ._schema import SchemaType
from ._settings import Settings


def load_from_environ(
    environ: Mapping[str, str] = os.environ,
    *,
    prefix: str = "CONFIG.",
    on_failure: Callable[[str, str | None], None] = lambda n, v: None,
) -> Settings:
    settings: Settings = {}

    for key, raw_value in environ.items():
        if key.startswith(prefix):
            names = key[len(prefix) :].split(".")
            target = settings
            for name in islice(names, len(names) - 1):
                try:
                    target = settings[name]
                    if not isinstance(target, dict):
                        target = settings[name] = {}
                except KeyError:
                    target = settings[name] = {}
            try:
                value = convert_string(raw_value)
            except ValueError:
                on_failure(arg, raw_value)
                continue
            target[names[-1]] = value

    return settings
