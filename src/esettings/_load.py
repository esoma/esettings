__all__ = ["load"]

import re
import sys
from collections import ChainMap
from logging import getLogger
from pathlib import Path
from typing import Any
from typing import Mapping

from platformdirs import user_data_dir

from ._argv import load_from_argv
from ._environ import load_from_environ
from ._file import load_from_file

_log = getLogger("esettings")


def load(
    application_name: str,
    application_author: str,
    *,
    default_settings: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    if default_settings is None:
        default_settings = {}
    else:
        default_settings = {**default_settings}
    assert isinstance(default_settings, dict)

    if application_name.strip():
        environ_prefix = re.sub(r"[\-\s_]+", "_", application_name.strip()).upper() + "_CONFIG."
    else:
        environ_prefix = "CONFIG."
    environ_settings = load_from_environ(prefix=environ_prefix, on_failure=_environ_on_failure)

    file_base_path = Path(user_data_dir(application_name, application_author))
    file_settings = load_from_file(file_base_path, on_failure=_file_on_failure)

    argv_settings = load_from_argv(on_extra=_argv_on_extra, on_failure=_argv_on_failure)

    return ChainMap(default_settings, environ_settings, file_settings, argv_settings)


def _environ_on_failure(key: str, value: str) -> None:
    _log.warning("ignoring invalid environment variable: %r", key)


def _file_on_failure(file_path: Path) -> None:
    _log.warning("ignoring invalid config file: %r", str(file_path))


def _argv_on_extra(argument: str) -> None:
    _log.error("argument %r was unexpected", argument)
    sys.exit(1)


def _argv_on_failure(argument: str, value: str | None) -> None:
    _log.warning("ignoring invalid argument: %r", argument)
