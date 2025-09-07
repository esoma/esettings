import sys
from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

import pytest

from esettings import load_from_argv


@pytest.fixture
def store_settings_mock():
    with patch("esettings._argv.store_settings") as mock:
        yield mock


def test_load_from_argv_default(store_settings_mock):
    with patch.object(sys, "argv", ["a", "--config.x", "1"]):
        settings = load_from_argv()
    assert settings == {}
    store_settings_mock.assert_has_calls([call(settings, "x", "1", ANY)])


def test_load_from_argv_empty():
    assert load_from_argv([]) == {}


def test_load_from_argv_basic(store_settings_mock):
    settings = load_from_argv(["--config.x", "1"])
    assert settings == {}
    store_settings_mock.assert_has_calls([call(settings, "x", "1", ANY)])


def test_load_from_argv_custom_prefix(store_settings_mock):
    settings = load_from_argv(["-my-prefix_x", "1"], prefix="-my-prefix_")
    assert settings == {}
    store_settings_mock.assert_has_calls([call(settings, "x", "1", ANY)])


def test_load_from_argv_custom_on_failure_missing():
    on_failure = MagicMock()
    assert load_from_argv(["--config.x"], on_failure=on_failure) == {}
    on_failure.assert_called_once_with("--config.x", None)


def test_load_from_argv_custom_on_failure_store_settings():
    on_failure = MagicMock()
    assert load_from_argv(["--config.x", "'"], on_failure=on_failure) == {}
    on_failure.assert_called_once_with("--config.x", "'")


def test_load_from_argv_custom_on_extra():
    on_extra = MagicMock()
    assert load_from_argv(["idk"], on_extra=on_extra) == {}
    on_extra.assert_called_once_with("idk")
