__all__ = ["Settings", "SettingsType"]

from typing import TypeAlias

SettingsType: TypeAlias = (
    "None | int | float | str | bool | list[SettingsType] | dict[str, SettingsType]"
)
Settings: TypeAlias = dict[str, SettingsType]
