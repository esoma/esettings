import os
from unittest.mock import patch

import pytest

from esettings import get_environment_variables_from_schema
from esettings import load_settings_from_environment


@pytest.mark.parametrize(
    "schema, expected_env_vars",
    [
        ({}, {}),
        ({("a",): (int,)}, {("a",): "A"}),
        ({("a b",): (int,)}, {("a b",): "A_B"}),
        ({("a-b",): (int,)}, {("a-b",): "A_B"}),
        ({("a_b",): (int,)}, {("a_b",): "A_B"}),
        ({("a", "b"): (int,)}, {("a", "b"): "A_B"}),
    ],
)
@pytest.mark.parametrize("prefix", [None, "TEST"])
def test_get_environment_variables_from_schema(schema, expected_env_vars, prefix):
    if prefix is not None:
        expected_env_vars = {name: f"{prefix}_{env}" for name, env in expected_env_vars.items()}
    assert get_environment_variables_from_schema(schema, prefix=prefix) == expected_env_vars


@pytest.mark.parametrize(
    "schema, env, expected_settings",
    [
        ({}, {}, {}),
        ({("a",): (None,)}, {"A": ""}, {"a": None}),
        ({("a",): (None,)}, {}, {}),
        ({("a",): (int,)}, {"A": "0"}, {"a": 0}),
        ({("a",): (int,)}, {"A": "-100"}, {"a": -100}),
        ({("a",): (int,)}, {"A": "100"}, {"a": 100}),
        ({("a",): (float,)}, {"A": "0"}, {"a": 0.0}),
        ({("a",): (float,)}, {"A": "-0.5"}, {"a": -0.5}),
        ({("a",): (float,)}, {"A": "0.5"}, {"a": 0.5}),
        ({("a",): (bool,)}, {"A": "false"}, {"a": False}),
        ({("a",): (bool,)}, {"A": "true"}, {"a": True}),
        ({("a",): (str,)}, {"A": ""}, {"a": ""}),
        ({("a",): (str,)}, {"A": "1"}, {"a": "1"}),
        ({("a",): (str,)}, {"A": "abc123"}, {"a": "abc123"}),
        ({("a",): (None, str)}, {"A": ""}, {"a": None}),
        ({("a",): (str, None)}, {"A": ""}, {"a": ""}),
        ({("a",): (list[str])}, {"A": ""}, {"a": [""]}),
        ({("a",): (list[str])}, {"A": "a,b, c "}, {"a": ["a", "b", " c "]}),
        ({("a",): (list[int])}, {"A": "0"}, {"a": [0]}),
        ({("a",): (list[int])}, {"A": "0, 4, -100   "}, {"a": [0, 4, -100]}),
        ({("a",): (list[None | str])}, {"A": ""}, {"a": [None]}),
        (
            {("a",): (list[None | int | float | bool | str])},
            {"A": ",1,1.5,false,doot"},
            {"a": [None, 1, 1.5, False, "doot"]},
        ),
        ({("a", "b"): (int,)}, {"A_B": "1"}, {"a": {"b": 1}}),
        ({("a",): (int, str)}, {"A": "a"}, {"a": "a"}),
        ({("a",): (int, bool)}, {"A": "a"}, {}),
        (
            {("a", "b"): (int,), ("a", "c"): (str,)},
            {"A_B": "1", "A_C": "2"},
            {"a": {"b": 1, "c": "2"}},
        ),
    ],
)
@pytest.mark.parametrize("prefix", [None, "TEST"])
def test_load_settings_from_environment(schema, env, expected_settings, prefix):
    if prefix is not None:
        env = {f"{prefix}_{key}": value for key, value in env.items()}
    with patch.dict(os.environ, env, clear=True):
        assert load_settings_from_environment(schema, prefix=prefix) == expected_settings
