import os
import sys
from io import BytesIO
from pathlib import Path
from pprint import pprint
from unittest.mock import patch

from platformdirs import user_data_dir

import alltoml

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
    'EXAMPLE_CONFIG.complex."env.name"': "'environ'",
    "EXAMPLE_CONFIG.complex.env.object": "{'a' = 1, 'b' = 1.0}",
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

# fmt: off
argv = [
    "example.py",
    "--config", "argv-specified-file.toml",
    "--config.argv", "'argv'",
    "--config.e", "'argv'",
    "--config.complex.\"argv.name\"", "'argv'",
    "--config.complex.argv.array", "[true, 1979-05-27T07:32:00Z]"
]
# fmt: on


def open_patch(path, *args, **kwargs):
    if path == Path("environ-specified-file.toml"):
        return BytesIO(environ_path_file.encode("utf8"))
    if path == Path("argv-specified-file.toml"):
        return BytesIO(argv_path_file.encode("utf8"))
    if path == Path(".") / "config.toml":
        return BytesIO(cwd_path_file.encode("utf8"))
    return BytesIO(user_path_file.encode("utf8"))


with (
    patch("alltoml._file.open", side_effect=open_patch),
    patch.object(os, "environ", environ),
    patch.object(sys, "argv", argv),
):
    config = alltoml.load("Example", "esoma", default_settings=defaults)
print(config)
print("--- defaults:")
pprint(defaults)
print("")
print("--- environ:")
pprint(environ)
print("")
print(f"--- user path file ({Path(user_data_dir('Example', 'esoma')) / 'config.toml'}):")
print(user_path_file.strip())
print("")
print(f"--- cwd path file ({Path('.') / 'config.toml'}):")
print(cwd_path_file.strip())
print("")
print("--- environ path file:")
print(environ_path_file.strip())
print("")
print("--- argv path file:")
print(argv_path_file.strip())
print("")
print("--- argv:")
pprint(argv)
print("")
print("--- results:")
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
print('complex."env.name" =', repr(config["complex"]["env.name"]))
print("complex.env.object =", repr(dict(config["complex"]["env"]["object"])))
print('complex."argv.name" =', repr(config["complex"]["argv.name"]))
print("complex.argv.array =", repr(config["complex"]["argv"]["array"]))
