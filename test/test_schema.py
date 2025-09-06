import pytest

from esettings import validate_schema


@pytest.mark.parametrize(
    "schema",
    [
        {},
        {
            ("a",): (None, int, float, str, bool),
            ("b",): (list[None | int | float | str | bool],),
            ("c",): (list[None], list[int], list[float], list[str], list[bool]),
            ("d",): (list[list[None | int | float | str | bool]],),
            ("e",): (
                list[list[None]],
                list[list[int]],
                list[list[float]],
                list[list[str]],
                list[list[bool]],
            ),
            ("f",): (str,),
            ("F", "g"): (int,),
        },
    ],
)
def test_valid_schema(schema):
    validate_schema(schema)


@pytest.mark.parametrize(
    "schema",
    [
        None,
        0,
        "a",
        [],
        {("a",): (object,)},
        {("a",): (dict[str, str],)},
        {("a",): (tuple[str],)},
        {("a",): (list,)},
        {("a",): (list[object],)},
        {"a": (int,)},
        {("a",): int},
        {("a",): (int,), ("a", "b"): (int,)},
        {("a_b",): (int,), ("a", "b"): (int,)},
        {("A",): (int,), ("a",): (int,)},
        {("!",): (int,)},
        {("a",): (int | str,)},
    ],
)
def test_invalid_schema(schema):
    with pytest.raises(Exception):
        validate_schema(schema)
