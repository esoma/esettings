from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from datetime import timezone
from math import inf
from math import isnan
from math import nan

import pytest

from esettings._convert import convert_string


@pytest.mark.parametrize(
    "input, output",
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
@pytest.mark.parametrize("extra", ["", "# test", "\n"])
def test_convert_string_basic(input, output, extra):
    assert convert_string(input + extra) == output


@pytest.mark.parametrize("input", ["nan", "+nan", "-nan"])
def test_convert_string_nan(input):
    assert isnan(convert_string(input))


@pytest.mark.parametrize(
    "input",
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
def test_convert_string_invalid(input):
    with pytest.raises(ValueError):
        convert_string(input)
