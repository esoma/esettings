# alltoml

`alltoml` parses [TOML](https://toml.io) from the environment and command line arguments to
simplify configuration.

Execute and inspect `example.py` for an example.


## load

```python
def load(
    application_name: str,
    application_author: str,
    *,
    default_settings: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    ...
```

`alltoml.load` is an opinionated way to load configuration from several sources with inheritance.

It first prioritizes values provided on the command line. This follows the behavior of
[alltoml.load_from_argv]("#load_from_argv"). Arguments should be prefixed with `--config.` to
appear in the output. Unexpected arguments (ones not prefixed with `--config.`) will cause the
program to exit with an error code of `1` and an error message. If there is a problem parsing an
argument then a warning is emitted and it is ignored.

Next a user specified config toml file is consulted. The file path may be specified using either an
environment variable or command line argument. The environment variable takes the form
`<APPLICATION_NAME>_CONFIG` (or just `CONFIG` if `application_name` is an empty string) and the
command line argument takes the form `--config`. If both are supplied then the command line
argument takes precedence. If no file is supplied or there is some error parsing the file a warning
is emitted and it is ignored.

Next a `config.toml` file in the current working directory is consulted. If the file is missing or
there is some error parsing the file a warning is emitted and it is ignored.

Next a `config.toml` in the user data directory for the application is consulted. The path of the
user data directory depends on the platform and `application_name` & `application_author` supplied.
If the file is missing or there is some error parsing the file a warning is emitted and it is
ignored.

Next environment variables are consulted. This follows the behavior of
[alltoml.load_from_environ]("#load_from_environ"). Environment variables are prefixed with
`<APPLICATION_NAME>_CONFIG.` (or just `CONFIG.` if `application_name` is an empty string). If there
is a problem parsing an environment variable then a warning is emitted and it is ignored.

Finally, the `default_settings` are used.

Note that nested mappings (objects/dicts) will transparently merge together in the order described
above. So if you have a default of:
```python
{ "my-object": { "a": 1 } }
```

And you specify the argument: `--config.my-object "{\"b\" = 2 }"` then the result is:
```python
{ "my-object": { "a": 1, "b": 2 } }
```


## load_from_argv

```python
def load_from_argv(
    argv: Iterable[str] | None = None,
    *,
    on_extra: Callable[[str], None] = lambda n: None,
    on_failure: Callable[[str, str | None], None] = lambda n, v: None,
    prefix: str = "--config.",
) -> dict[str, Any]:
    ...
```

`alltoml.load_from_argv` parses TOML from command line arguments.

`argv` are the arguments to parse. By default this will be the arguments from `sys.argv`. Note that
when passing `argv` directly that the first value (the name of the python script executed) should
be removed.
`on_extra` is a callback that occurs when an unexpected argument is found. The argument supplied is
the unexpected argument name. The default behavior is that the argument is ignored.
`on_failure` is a callback that occurs when an argument fails to parse (either its name or value is
incorrect). The first argument is the argument name and the second is the argument value. The
argument value is `None` when there is no value following the argument. The default behavior is
that the argument is ignored.
`prefix` is the prefix for an argument for it to be expected. Arguments that don't start with this
prefix trigger the `on_extra` callback.


## load_from_environ

```python
def load_from_environ(
    environ: Mapping[str, str] | None = None,
    *,
    prefix: str = "CONFIG.",
    on_failure: Callable[[str, str], None] = lambda n, v: None,
) -> dict[str, Any]:
    ...
```

`alltoml.load_from_environ` parses TOML from environment variables.

`environ` is a `os.environ`-like mapping of environment variables to parse. By default this is
`os.environ`.
`prefix` is the prefix for an environment variable to be picked up and parsed.
`on_failure` is a callback that occurs when an environment variable fails to parse (either its key
or value is incorrect). The first argument is the key and the second is the value. The default
behavior is that the environment variable is ignored.


## load_from_file

```python
def load_from_file(
    base_path: Path,
    *,
    name: Path = Path("config.toml"),
    on_failure: Callable[[Path], None] = lambda p: None,
) -> dict[str, Any]:
    ...
```

`alltoml.load_from_file` parses TOML from a file.

`base_path` is the path to look for the config file.
`name` is the name of the file to load. This defaults to `config.toml`.
`on_failure` is a callback that occurs when the file fails to parse, cannot be found or cannot be
opened. The only argument is the path to the file that was attempted to be loaded. The default
behavior is that the file is ignored (an empty mapping is returned).
