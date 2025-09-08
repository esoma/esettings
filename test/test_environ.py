import os
from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

import pytest

from alltoml import load_from_environ


@pytest.fixture
def store_settings_mock():
    with patch("alltoml._environ.store_settings") as mock:
        yield mock


def test_load_from_environ_default(store_settings_mock):
    with patch.object(os, "environ", {"CONFIG.x": "1"}):
        settings = load_from_environ()
    assert settings == {}
    store_settings_mock.assert_has_calls([call(settings, "x", "1", ANY)])


def test_load_from_environ_empty():
    assert load_from_environ({}) == {}


def test_load_from_environ_basic(store_settings_mock):
    settings = load_from_environ({"CONFIG.x": "1"})
    assert settings == {}
    store_settings_mock.assert_has_calls([call(settings, "x", "1", ANY)])


def test_load_from_argv_custom_prefix(store_settings_mock):
    settings = load_from_environ({"myprefix_x": "1"}, prefix="myprefix_")
    assert settings == {}
    store_settings_mock.assert_has_calls([call(settings, "x", "1", ANY)])


def test_load_from_environ_custom_on_failure_store_settings():
    on_failure = MagicMock()
    assert load_from_environ({"CONFIG.x": "'"}, on_failure=on_failure) == {}
    on_failure.assert_called_once_with("CONFIG.x", "'")
