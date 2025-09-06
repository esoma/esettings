__all__ = ["Schema", "SchemaType", "validate_schema"]

import re
from collections import Counter
from types import NoneType
from types import UnionType
from typing import Any
from typing import Final
from typing import Mapping
from typing import TypeAlias
from typing import Union
from typing import get_args as get_typing_args
from typing import get_origin as get_typing_origin

SchemaType: TypeAlias = "None | int | float | str | bool | list[SchemaType]"
Schema: TypeAlias = Mapping[tuple[str, ...], tuple[type[SchemaType], ...]]


def validate_schema(schema: Schema) -> None:
    for name, types in schema.items():
        if not isinstance(name, tuple):
            raise RuntimeError(f"invalid name: {name}")
        if name[:-1] in schema:
            raise RuntimeError(f"{name[:-1]} is both an mapping and a property")
        _validate_name(name)
        _validate_types(types)

    normalized_names: dict[str, list[tuple[str, ...]]] = {}
    for name in schema:
        normalized_name = (
            "-".join(name).upper().replace("-", "-").replace("_", "-").replace(" ", "-")
        )
        try:
            names = normalized_names[normalized_name]
        except KeyError:
            names = normalized_names[normalized_name] = []
        names.append(name)
    for names in normalized_names.values():
        if len(names) > 1:
            raise RuntimeError(f"conflicting names: {', '.join(repr(n) for n in names)}")


_NAME_COMPONENT_PATTERN: Final = re.compile(r"^[a-zA-Z0-9\-\_\s]+$")


def _validate_name(name: tuple[Any, ...]) -> None:
    for component in name:
        if not _NAME_COMPONENT_PATTERN.match(component):
            raise RuntimeError(f"invalid name component: {name}")


_VALID_TYPES: Final = {NoneType, int, float, str, bool}


def _validate_types(types: tuple[Any, ...]) -> None:
    for type in types:
        base_type = get_typing_origin(type)
        if base_type is None:
            base_type = type
        if base_type is None:
            base_type = NoneType
        if base_type == list:
            try:
                typing_arg = get_typing_args(type)[0]
            except IndexError:
                raise RuntimeError("list is missing type specifier")
            if get_typing_origin(typing_arg) in (Union, UnionType):
                sub_types = get_typing_args(typing_arg)
            else:
                sub_types = (typing_arg,)
            _validate_types(sub_types)
        else:
            if base_type not in _VALID_TYPES:
                raise RuntimeError(f"invalid type: {type}")
