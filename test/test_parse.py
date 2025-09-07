from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from datetime import timezone
from math import inf
from math import isnan
from math import nan
from unittest.mock import ANY
from unittest.mock import MagicMock

import pytest

from esettings._parse import store_settings


@pytest.mark.parametrize(
    "raw_value, expected_value",
    [
        ("''", ""),
        ('""', ""),
        ("''''''", ""),
        ('""""""', ""),
        ("'''a\nb'''", "a\nb"),
        ('"""a\nb"""', "a\nb"),
        ("'\\t'", "\\t"),
        ('"\\t"', "\t"),
        ("0", 0),
        ("+99", 99),
        ("-17", -17),
        ("1_000", 1000),
        ("0xDEADBEEF", 0xDEADBEEF),
        ("0o01234567", 0o01234567),
        ("0b11010110", 0b11010110),
        ("+1.0", 1.0),
        ("3.1415", 3.1415),
        ("-0.01", -0.01),
        ("5e+22", 5e22),
        ("1e06", 1e06),
        ("-2E-2", -2e-2),
        ("6.626e-34", 6.626e-34),
        ("224_617.445_991_228", 224_617.445_991_228),
        ("inf", inf),
        ("+inf", +inf),
        ("-inf", -inf),
        ("true", True),
        ("false", False),
        (
            "1979-05-27T07:32:00Z",
            datetime(year=1979, month=5, day=27, hour=7, minute=32, tzinfo=timezone.utc),
        ),
        (
            "1979-05-27T07:32:00.999999-07:00",
            datetime(
                year=1979,
                month=5,
                day=27,
                hour=7,
                minute=32,
                microsecond=999999,
                tzinfo=timezone(timedelta(hours=-7)),
            ),
        ),
        (
            "1979-05-27 07:32:00Z",
            datetime(year=1979, month=5, day=27, hour=7, minute=32, tzinfo=timezone.utc),
        ),
        (
            "1979-05-27T07:32:00.999999",
            datetime(year=1979, month=5, day=27, hour=7, minute=32, microsecond=999999),
        ),
        ("1979-05-27", date(year=1979, month=5, day=27)),
        ("07:32:01", time(hour=7, minute=32, second=1)),
        ("07:32:01.999999", time(hour=7, minute=32, second=1, microsecond=999999)),
        ("[]", []),
        ("[1,2,\n3,  4]", [1, 2, 3, 4]),
        ("[1, '1', 1.0]", [1, "1", 1.0]),
        ("{}", {}),
        ("{ x = 1, y = 2}", {"x": 1, "y": 2}),
        ("{x='a',  y  =  4  }", {"x": "a", "y": 4}),
    ],
)
@pytest.mark.parametrize("extra_value", ["", "# test", "\n"])
@pytest.mark.parametrize(
    "raw_key, expected_key",
    [
        ("a", ("a",)),
        ("a.b", ("a", "b")),
        ("   a    .    b   ", ("a", "b")),
        ("'a'.'b'", ("a", "b")),
        ('"a"."b"', ("a", "b")),
        ("'a.b'", ("a.b",)),
        ('"a.b"', ("a.b",)),
        ('"a\\""."b"', ('a"', "b")),
        ("[a]\nb", ("a", "b")),
        ("[a.b]\nc", ("a", "b", "c")),
        ("0", ("0",)),
    ],
)
def test_store_settings_basic(raw_value, expected_value, extra_value, raw_key, expected_key):
    expected_settings = target = {}
    for name in expected_key[:-1]:
        target = expected_settings.setdefault(name, {})
    target[expected_key[-1]] = expected_value

    settings = {}
    store_settings(settings, raw_key, raw_value + extra_value, lambda: None)
    assert settings == expected_settings


@pytest.mark.parametrize("input", ["nan", "+nan", "-nan"])
def test_store_settings_nan(input):
    settings = {}
    store_settings(settings, "a", input, lambda: None)
    assert settings == {"a": ANY}
    assert isnan(settings["a"])


@pytest.mark.parametrize(
    "raw_value",
    [
        "'",
        "'''",
        '"',
        '"""',
        "''''",
        '""""',
        "'\n'",
        '"\n"',
        "''\n1",
        "{\n}",
        "''\nvalue = 12",
        "''\nx = 12",
    ],
)
def test_store_settings_invalid_value(raw_value):
    def _():
        raise RuntimeError()

    settings = {}
    with pytest.raises(RuntimeError):
        store_settings(settings, "a", raw_value, _)
    assert settings == {}


@pytest.mark.parametrize(
    "raw_key",
    [
        "",
        "'",
        "'''",
        '"',
        '"""',
        "''''",
        '""""',
        "'\n'",
        '"\n"',
        "''\n1",
        "{\n}",
        "[hello]",
        "[hello]x",
        "[[hello]]",
        "[[hello]]\nx",
        "a=",
        "a = 0",
        "a=0\nb",
    ],
)
def test_store_settings_invalid_key(raw_key):
    def _():
        raise RuntimeError()

    settings = {}
    with pytest.raises(RuntimeError):
        store_settings(settings, raw_key, "0", _)
    assert settings == {}


def test_store_settings_dict_overwrite():
    fail_mock = MagicMock()
    settings = {"a": {}}
    store_settings(settings, "a", "0", fail_mock)
    assert settings == {"a": {}}
    fail_mock.assert_called_once()


def test_store_settings_not_dict_overwrite():
    fail_mock = MagicMock()
    settings = {"a": 1}
    store_settings(settings, "a.b", "2", fail_mock)
    assert settings == {"a": 1}
    fail_mock.assert_called_once()
