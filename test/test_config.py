import os
from dataclasses import dataclass
from enum import IntEnum
from enum import StrEnum
from pathlib import Path
from unittest.mock import patch

import pytest
from e16 import Config
from e16 import load_config
from e16._config import _load_env
from e16._config import _sanitize_env_key
from platformdirs import user_data_dir
from platformdirs import user_log_dir


@pytest.fixture
def env():
    with patch.dict(os.environ, clear=True):
        yield os.environ


def test_config():
    @dataclass
    class TestConfig(Config):
        pass

    with load_config("a", "b", TestConfig) as config:
        assert config.application.name == "a"
        assert config.application.author == "b"
        assert config.application.user_data_path == Path(user_data_dir("a", "b"))
        assert config.application.user_log_path == Path(user_log_dir("a", "b"))


def test_load_env(env):
    class StrEnumConfig(StrEnum):
        A = "strenumval"

    class IntEnumConfig(IntEnum):
        ZERO = 0

    @dataclass
    class SubConfig:
        abc: str

    @dataclass
    class TestConfig(Config):
        missing_var: str
        str_var: str
        path_var: Path
        int_var: int
        float_var: float
        bool_var: bool
        strenum_var: StrEnumConfig
        intenum_var: IntEnumConfig
        sub: SubConfig

    env["TEST_APPLICATION_NAME"] = "A"
    env["TEST_APPLICATION_AUTHOR"] = "B"
    env["TEST_APPLICATION_USER_DATA_PATH"] = "C"
    env["TEST_APPLICATION_USER_LOG_PATH"] = "D"

    env["TEST_STR_VAR"] = "abc"
    env["TEST_PATH_VAR"] = "def"
    env["TEST_INT_VAR"] = "1"
    env["TEST_FLOAT_VAR"] = "0.1"
    env["TEST_BOOL_VAR"] = "false"
    env["TEST_STRENUM_VAR"] = "strenumval"
    env["TEST_INTENUM_VAR"] = "0"
    env["TEST_SUB_ABC"] = "xyz"

    result = _load_env("TEST", TestConfig)
    assert result == {
        "application": {},
        "str_var": "abc",
        "path_var": Path("def"),
        "int_var": 1,
        "float_var": 0.1,
        "bool_var": False,
        "strenum_var": StrEnumConfig.A,
        "intenum_var": IntEnumConfig.ZERO,
        "sub": {"abc": "xyz"},
    }


@pytest.mark.parametrize(
    "input, output",
    [
        ("a", "A"),
        ("   a    ", "A"),
        ("a'b", "AB"),
        ("a b", "A_B"),
        ("a-b", "A_B"),
        ("A_B", "A_B"),
        ("ahzAHZ059", "AHZAHZ059"),
        ("_A_", "A"),
    ],
)
def test_sanitize_env_key(input, output):
    assert _sanitize_env_key(input) == output
