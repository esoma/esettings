__all__ = ["Schema", "SchemaType"]

from typing import Mapping
from typing import TypeAlias

SchemaType: TypeAlias = "None | int | float | str | bool | list[SchemaType]"
Schema: TypeAlias = Mapping[tuple[str, ...], tuple[type[SchemaType], ...]]


"""
def build_schema(annotation: Any) -> Schema:
    return Schema(tuple(_build_settings(annotation, (), ())))


def _build_settings(annotation: Any, name: tuple[str, ...], metadata: tuple[Any, ...]) -> Generator[SettingSchema, None, None]:
    types, metadata = _resolve_annotation(annotation)
    yield SettingSchema(
        name,
        types,
        metadata
    )


def _resolve_annotation(type: Any) -> tuple[tuple[type, ...], tuple[Any, ...]]:
    if hasattr(type, "__origin__") and hasattr(type, "__metadata__"):
        return (_resolve_union(type.__origin__), type.__metadata__)
    return (_resolve_union(type), ())

def _resolve_union(type: Any) -> tuple[type, ...]:
    if get_origin(type) in (Union, UnionType):
        return get_args(type)
    return (type,)
"""
