__all__ = ["Settings", "SettingsType"]

from typing import TypeAlias

from ._schema import SchemaType

SettingsType: TypeAlias = "SchemaType | dict[str, SchemaType]"
Settings: TypeAlias = dict[str, SettingsType]
