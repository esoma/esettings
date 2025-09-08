import os
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import esettings

defaults = {
    "default": "default",
    "a": "default",
    "b": "default",
    "c": "default",
    "d": "default",
    "e": "default",
}

environ = {
    "EXAMPLE_CONFIG": "environ-specified-file.toml",
    "EXAMPLE_CONFIG.environ": "'environ'",
    "EXAMPLE_CONFIG.a": "'environ'",
}

user_path_file = """
user_path_file = "user-path-file"
b = "user-path-file"
c = "user-path-file"
d = "user-path-file"
e = "user-path-file"
"""

cwd_path_file = """
cwd_path_file = "cwd-path-file"
c = "cwd-path-file"
d = "user-path-file"
e = "user-path-file"
"""

environ_path_file = """
path_file = "environ-path-file"
d = "user-path-file"
e = "user-path-file"
"""

argv_path_file = """
path_file = "argv-path-file"
d = "argv-path-file"
e = "argv-path-file"
"""

argv = [
    "example.py",
    # fmt: off
    "--config",
    "argv-specified-file.toml",
    "--config.argv",
    "'argv'",
    "--config.e",
    "'argv'",
    # fmt: on
]


def open_patch(path, *args, **kwargs):
    if path == Path("environ-specified-file.toml"):
        return BytesIO(environ_path_file.encode("utf8"))
    if path == Path("argv-specified-file.toml"):
        return BytesIO(argv_path_file.encode("utf8"))
    if path == Path(".") / "config.toml":
        return BytesIO(cwd_path_file.encode("utf8"))
    return BytesIO(user_path_file.encode("utf8"))


with (
    patch("esettings._file.open", side_effect=open_patch),
    patch.object(os, "environ", environ),
    patch.object(sys, "argv", argv),
):
    config = esettings.load("Example", "esoma", default_settings=defaults)

print("---------------")
print("default =", repr(config["default"]))
print("user_path_file =", repr(config["user_path_file"]))
print("cwd_path_file =", repr(config["cwd_path_file"]))
print("path_file =", repr(config["path_file"]))
print("environ =", repr(config["environ"]))
print("argv =", repr(config["argv"]))
print("a =", repr(config["a"]))
print("b =", repr(config["b"]))
print("c =", repr(config["c"]))
print("d =", repr(config["d"]))
print("e =", repr(config["e"]))
