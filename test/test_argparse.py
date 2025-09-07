from argparse import ArgumentParser
from unittest.mock import MagicMock

import pytest

from esettings import build_argument_parser
from esettings import load_settings_from_argument_parser


@pytest.mark.parametrize(
    "schema, args, expected_settings",
    [
        ({}, [], {}),
        ({("a",): (None,)}, ["--a"], {"a": None}),
        ({("a",): (None,)}, [], {}),
        ({("a",): (int,)}, ["--a", "0"], {"a": 0}),
        ({("a",): (int,)}, ["--a", "-100"], {"a": -100}),
        ({("a",): (int,)}, ["--a", "100"], {"a": 100}),
        ({("a",): (float,)}, ["--a", "0"], {"a": 0.0}),
        ({("a",): (float,)}, ["--a", "-0.5"], {"a": -0.5}),
        ({("a",): (float,)}, ["--a", "0.5"], {"a": 0.5}),
        ({("a",): (bool,)}, ["--a", "false"], {"a": False}),
        ({("a",): (bool,)}, ["--a", "true"], {"a": True}),
        ({("a",): (str,)}, ["--a", ""], {"a": ""}),
        ({("a",): (str,)}, ["--a", "1"], {"a": "1"}),
        ({("a",): (str,)}, ["--a", "abc123"], {"a": "abc123"}),
        ({("a",): (None, str)}, ["--a", ""], {"a": None}),
        ({("a",): (str, None)}, ["--a", ""], {"a": ""}),
        ({("a",): (list[str])}, ["--a", ""], {"a": [""]}),
        ({("a",): (list[str])}, ["--a", "a,b, c "], {"a": ["a", "b", " c "]}),
        ({("a",): (list[int])}, ["--a", "0"], {"a": [0]}),
        ({("a",): (list[int])}, ["--a", "0, 4, -100"], {"a": [0, 4, -100]}),
        ({("a",): (list[None | str])}, ["--a", ""], {"a": [None]}),
        (
            {("a",): (list[None | int | float | bool | str])},
            ["--a", ",1,1.5,false,doot"],
            {"a": [None, 1, 1.5, False, "doot"]},
        ),
        ({("a", "b"): (int,)}, ["--a-b", "1"], {"a": {"b": 1}}),
        ({("a",): (int, str)}, ["--a", "a"], {"a": "a"}),
        ({("a",): (int, bool)}, ["--a", "a"], {}),
        ({("a",): (list[int],)}, ["--a", "a"], {}),
        (
            {("a", "b"): (int,), ("a", "c"): (str,)},
            ["--a-b", "1", "--a-c", "2"],
            {"a": {"b": 1, "c": "2"}},
        ),
    ],
)
def test_load_settings_from_argument_parser(schema, args, expected_settings):
    argparser = ArgumentParser()
    build_argument_parser(argparser, schema)
    namespace = argparser.parse_args(args)
    assert load_settings_from_argument_parser(namespace, schema) == expected_settings


def test_load_settings_from_argument_parser_on_failure():
    schema = {("a",): (int,)}
    on_failure_mock = MagicMock()
    argparser = ArgumentParser()
    build_argument_parser(argparser, schema)
    namespace = argparser.parse_args(["--a", "x"])
    load_settings_from_argument_parser(namespace, schema, on_failure=on_failure_mock)
    on_failure_mock.assert_called_once_with(("a",), "x")


@pytest.mark.parametrize(
    "schema, args", [({("a",): (object,)}, ["--a", "a"]), ({("a",): (list,)}, ["--a", "a"])]
)
def test_load_settings_from_argument_parser_error(schema, args):
    argparser = ArgumentParser()
    build_argument_parser(argparser, schema)
    namespace = argparser.parse_args(args)
    with pytest.raises(Exception):
        load_settings_from_argument_parser(namespace, schema)
