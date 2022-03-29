import os
import json
from appdirs import user_config_dir

def config_dir() -> str:
    path = user_config_dir("labbot")
    os.makedirs(path, exist_ok=True)

    return path

def write_config(name: str, data: dict) -> None:
    conf_path = os.path.join(config_dir(), f"{name}.json")

    with open(conf_path, "w") as file:
        json.dump(data, file)

    if data != read_config(name):
        raise ValueError("Config could not be saved properly")

def read_config(name: str) -> dict:
    conf_path = os.path.join(config_dir(), f"{name}.json")

    try:
        with open(conf_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}