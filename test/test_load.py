import logging
from collections import ChainMap
from pathlib import Path
from unittest.mock import patch

import pytest
from platformdirs import user_data_dir

from esettings import load
from esettings._load import _argv_on_extra
from esettings._load import _argv_on_failure
from esettings._load import _environ_on_failure
from esettings._load import _file_on_failure


def test_environ_on_failure(caplog):
    caplog.set_level(logging.INFO)
    _environ_on_failure("a", "b")
    assert caplog.record_tuples == [
        ("esettings", logging.WARNING, "ignoring invalid environment variable: %r" % ("a",))
    ]


def test_file_on_failure(caplog):
    caplog.set_level(logging.INFO)
    _file_on_failure(Path("a/b"))
    assert caplog.record_tuples == [
        ("esettings", logging.WARNING, "ignoring invalid config file: %r" % (str(Path("a/b")),))
    ]


def test_argv_on_extra(caplog):
    caplog.set_level(logging.INFO)
    with pytest.raises(SystemExit) as excinfo:
        _argv_on_extra("a")
    assert excinfo.value.args == (1,)
    assert caplog.record_tuples == [
        ("esettings", logging.ERROR, "argument %r was unexpected" % ("a",))
    ]


def test_argv_on_failure(caplog):
    caplog.set_level(logging.INFO)
    _argv_on_failure("a", "b")
    assert caplog.record_tuples == [
        ("esettings", logging.WARNING, "ignoring invalid argument: %r" % ("a",))
    ]


@pytest.mark.parametrize(
    "application_name, environ_prefix",
    [
        ("a", "A_CONFIG."),
        ("    a    ", "A_CONFIG."),
        ("  a   -   b    c-d _  e   ", "A_B_C_D_E_CONFIG."),
        ("", "CONFIG."),
        ("    ", "CONFIG."),
        ("   -   ", "__CONFIG."),
    ],
)
@pytest.mark.parametrize("application_author", ["a", "b"])
def test_load(application_name, application_author, environ_prefix):
    with (
        patch("esettings._load.load_from_environ") as load_from_environ_mock,
        patch("esettings._load.load_from_file") as load_from_file_mock,
        patch("esettings._load.load_from_argv") as load_from_argv_mock,
    ):
        settings = load(application_name, application_author)

    load_from_environ_mock.assert_called_once_with(
        prefix=environ_prefix, on_failure=_environ_on_failure
    )

    load_from_file_mock.assert_called_once_with(
        Path(user_data_dir(application_name, application_author)), on_failure=_file_on_failure
    )

    load_from_argv_mock.assert_called_once_with(
        on_extra=_argv_on_extra, on_failure=_argv_on_failure
    )

    assert isinstance(settings, ChainMap)
    assert settings.maps == [
        {},
        load_from_environ_mock.return_value,
        load_from_file_mock.return_value,
        load_from_argv_mock.return_value,
    ]
