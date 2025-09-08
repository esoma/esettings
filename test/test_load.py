import logging
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

import pytest
from deep_chainmap import DeepChainMap
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
    "application_name, environ_prefix, environ_config_key",
    [
        ("a", "A_CONFIG.", "A_CONFIG"),
        ("    a    ", "A_CONFIG.", "A_CONFIG"),
        ("  a   -   b    c-d _  e   ", "A_B_C_D_E_CONFIG.", "A_B_C_D_E_CONFIG"),
        ("", "CONFIG.", "CONFIG"),
        ("    ", "CONFIG.", "CONFIG"),
        ("   -   ", "__CONFIG.", "__CONFIG"),
    ],
)
@pytest.mark.parametrize("application_author", ["a", "b"])
@pytest.mark.parametrize("argv_config", [None, "myconfig.toml", "dir/myconf.toml"])
@pytest.mark.parametrize("environ_config", [None, "myenvconfig.toml", "dir2/myenvconf.toml"])
@pytest.mark.parametrize("default_settings", [None, {"a": "b"}])
def test_load(
    application_name,
    application_author,
    environ_prefix,
    environ_config_key,
    argv_config,
    environ_config,
    default_settings,
):
    argv = ["test"]
    environ = {}

    expected_default_settings = {}
    if default_settings is not None:
        expected_default_settings = {**default_settings}

    file_settings = {}
    if environ_config:
        environ[environ_config_key] = environ_config
        file_settings = MagicMock(name="env_file_settings")
    if argv_config:
        argv.extend(["--config", argv_config])
        file_settings = MagicMock(name="argv_file_settings")

    cwd_file_settings = MagicMock(name="cwd_file_settings")
    user_file_settings = MagicMock(name="user_file_settings")

    def load_from_file(path, *args, name=None, **kwargs):
        if (
            argv_config is not None
            and path == Path(argv_config).parent
            and name == Path(Path(argv_config).name)
        ):
            assert file_settings._extract_mock_name() == "argv_file_settings"
            return file_settings
        if (
            environ_config is not None
            and path == Path(environ_config).parent
            and name == Path(Path(environ_config).name)
        ):
            assert file_settings._extract_mock_name() == "env_file_settings"
            return file_settings
        if path == Path("."):
            return cwd_file_settings
        return user_file_settings

    with (
        patch("esettings._load.load_from_environ") as load_from_environ_mock,
        patch("esettings._load.load_from_file", side_effect=load_from_file) as load_from_file_mock,
        patch("esettings._load.load_from_argv") as load_from_argv_mock,
        patch.object(sys, "argv", argv),
        patch.object(os, "environ", environ),
    ):
        kwargs = {}
        if default_settings is not None:
            kwargs["default_settings"] = default_settings
        settings = load(application_name, application_author, **kwargs)

    load_from_environ_mock.assert_called_once_with(
        prefix=environ_prefix, on_failure=_environ_on_failure
    )

    load_from_file_mock.assert_has_calls(
        [
            call(
                Path(user_data_dir(application_name, application_author)),
                on_failure=_file_on_failure,
            ),
            call(Path("."), on_failure=_file_on_failure),
        ]
        + (
            [
                call(
                    Path(argv_config).parent,
                    name=Path(Path(argv_config).name),
                    on_failure=_file_on_failure,
                )
            ]
            if argv_config
            else []
        ),
        any_order=True,
    )

    load_from_argv_mock.assert_called_once_with(
        [], on_extra=_argv_on_extra, on_failure=_argv_on_failure
    )

    assert isinstance(settings, DeepChainMap)
    assert settings.maps == [
        load_from_argv_mock.return_value,
        file_settings,
        cwd_file_settings,
        user_file_settings,
        load_from_environ_mock.return_value,
        expected_default_settings,
    ]
    assert settings.maps[-1] is not default_settings


def test_load_invalid_config_argv(caplog):
    caplog.set_level(logging.INFO)
    with patch.object(sys, "argv", ["test", "--config"]):
        with pytest.raises(SystemExit) as excinfo:
            load("", "")
        assert excinfo.value.args == (1,)
    assert caplog.record_tuples == [
        ("esettings", logging.ERROR, "argument %r has no value" % ("--config",))
    ]
