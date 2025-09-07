from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

import pytest

from esettings import load_from_argv


@pytest.fixture
def convert_string_mock():
    with patch("esettings._argv.convert_string") as convert_string_mock:
        yield convert_string_mock


def test_load_from_argv_empty():
    assert load_from_argv(["name"]) == {}


def test_load_from_argv_basic(convert_string_mock):
    RETURN_VALUE = object()

    def _(raw_value):
        if raw_value == "'":
            raise ValueError()
        return RETURN_VALUE

    convert_string_mock.side_effect = _
    assert load_from_argv(["name", "--config.x", "1", "x", "--config.y", "'"]) == {
        "x": RETURN_VALUE
    }
    convert_string_mock.assert_has_calls([call("1"), call("'")])


def test_load_from_argv_overwrite_with_dict(convert_string_mock):
    assert load_from_argv(["name", "--config.x", "1", "--config.x.y", "1"]) == {
        "x": {"y": convert_string_mock.return_value}
    }


def test_load_from_argv_overwrite_with_value(convert_string_mock):
    assert load_from_argv(["name", "--config.x.y", "1", "--config.x", "1"]) == {
        "x": convert_string_mock.return_value
    }


def test_load_from_argv_custom_prefix(convert_string_mock):
    assert load_from_argv(["name", "-my-prefix_x", "1"], prefix="-my-prefix_") == {
        "x": convert_string_mock.return_value
    }
    convert_string_mock.assert_called_once_with("1")


def test_load_from_argv_custom_on_extra():
    on_extra = MagicMock()
    assert load_from_argv(["name", "idk"], on_extra=on_extra) == {}
    on_extra.assert_called_once_with("idk")


def test_load_from_argv_custom_on_failure_string():
    on_failure = MagicMock()
    assert load_from_argv(["name", "--config.x", "'"], on_failure=on_failure) == {}
    on_failure.assert_called_once_with("--config.x", "'")


def test_load_from_argv_custom_on_failure_missing():
    on_failure = MagicMock()
    assert load_from_argv(["name", "--config.x"], on_failure=on_failure) == {}
    on_failure.assert_called_once_with("--config.x", None)
