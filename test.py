import os

from esettings._argparse import load_settings_from_argv


def on_failure(n):
    print(f"{n} extra")


s = load_settings_from_argv(on_failure=on_failure)
print(s)
