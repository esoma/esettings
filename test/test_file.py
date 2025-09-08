import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import tomllib

from esettings import load_from_file


@pytest.fixture
def base_path():
    with tempfile.TemporaryDirectory() as dir:
        yield Path(dir)


def test_load_from_file_default(base_path):
    with (
        patch("esettings._file.open") as open_mock,
        patch.object(tomllib, "load") as tomllib_load_mock,
    ):
        assert load_from_file(base_path) == tomllib_load_mock.return_value
    open_mock.assert_called_once_with(base_path / "config.toml", "rb", encoding="utf8")
    tomllib_load_mock.assert_called_once_with(open_mock.return_value.__enter__.return_value)


def test_load_from_file_custom_name(base_path):
    with (
        patch("esettings._file.open") as open_mock,
        patch.object(tomllib, "load") as tomllib_load_mock,
    ):
        assert load_from_file(base_path, name=Path("myconfig")) == tomllib_load_mock.return_value
    open_mock.assert_called_once_with(base_path / "myconfig", "rb", encoding="utf8")
    tomllib_load_mock.assert_called_once_with(open_mock.return_value.__enter__.return_value)


@pytest.mark.parametrize(
    "ex", [OSError, FileNotFoundError, PermissionError, tomllib.TOMLDecodeError]
)
def test_load_from_file_error_default(base_path, ex):
    with patch("esettings._file.open", side_effect=ex) as open_mock:
        assert load_from_file(base_path) == {}


@pytest.mark.parametrize(
    "ex", [OSError, FileNotFoundError, PermissionError, tomllib.TOMLDecodeError]
)
def test_load_from_file_error_default(base_path, ex):
    on_failure = MagicMock()
    with patch("esettings._file.open", side_effect=ex) as open_mock:
        assert load_from_file(base_path, on_failure=on_failure) == {}
    on_failure.assert_called_once_with()
