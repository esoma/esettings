import os

from esettings import Schema
from esettings import get_environment_variables_from_schema
from esettings import load_settings_from_environment
from esettings import validate_schema

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
validate_schema(schema)

print(get_environment_variables_from_schema(schema, prefix="DOORLORD"))
env_settings = load_settings_from_environment(schema, prefix="DOORLORD")
print(env_settings)
