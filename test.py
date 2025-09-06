import os

from esettings import Schema
from esettings import load_settings_from_environment

os.environ["DOORLORD_X"] = "0"
os.environ["DOORLORD_Y"] = ""
os.environ["DOORLORD_SUB_IF_A"] = "true,false,ok"
os.environ["DOORLORD_SUB_IF_B"] = "true,false,ok"

schema: Schema = {
    ("x",): (int,),
    ("y",): (None, str),
    ("sub_if", "a"): (list[bool | str],),
    ("sub_if", "b"): (list[bool], list[str]),
}

env_settings = load_settings_from_environment(schema, prefix="DOORLORD")
print(env_settings)
