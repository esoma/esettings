__all__ = ["load_from_argv"]

import sys
from itertools import islice
from typing import Any
from typing import Callable
from typing import Sequence

from ._convert import convert_string


def load_from_argv(
    argv: Sequence[str] = sys.argv,
    *,
    on_extra: Callable[[str], None] = lambda n: None,
    on_failure: Callable[[str, str | None], None] = lambda n, v: None,
    prefix: str = "--config.",
) -> dict[str, Any]:
    settings: dict[str, Any] = {}

    argv_i = iter(argv)
    next(argv_i)
    while True:
        try:
            arg = next(argv_i)
        except StopIteration:
            break
        if arg.startswith(prefix):
            names = arg[len(prefix) :].split(".")
            target = settings
            for name in islice(names, len(names) - 1):
                try:
                    target = settings[name]
                    if not isinstance(target, dict):
                        target = settings[name] = {}
                except KeyError:
                    target = settings[name] = {}
            try:
                raw_value: str = next(argv_i)
            except StopIteration:
                on_failure(arg, None)
                continue
            try:
                value = convert_string(raw_value)
            except ValueError:
                on_failure(arg, raw_value)
                continue
            target[names[-1]] = value
        else:
            on_extra(arg)

    return settings
