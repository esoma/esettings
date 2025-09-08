__all__ = ["load_from_file"]

from pathlib import Path
from typing import Any
from typing import Callable

import tomllib


def load_from_file(
    base_path: Path,
    *,
    name: Path = Path("config.toml"),
    on_failure: Callable[[], None] = lambda: None,
) -> dict[str, Any]:
    try:
        with open(base_path / name, "rb", encoding="utf8") as file:
            return tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        on_failure()
    return {}
