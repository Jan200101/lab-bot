import os
import json
from typing import List, Dict, Any
from appdirs import user_config_dir  # type: ignore

CONFIG_FILE = "config.json"

class _ConfigDict:

    def __init__(self, conf_name: str, **kwargs):
        pass

class Config:

    def __init__(self, conf_name):
        self.conf_name = conf_name

        self.default_global_data = {}
        self.default_group_data = {}
        self.default_repo_data = {}


    def group(self, id):
        pass

    def repo(self, id):
        pass

    def default_global(self, **kwargs):
        self.default_global_data = kwargs

    def default_group(self, **kwargs):
        self.default_group_data = kwargs

    def default_repo(self, **kwargs):
        self.default_repo_data = kwargs

def list_instances() -> List[str]:
    instances = []
    with os.scandir(config_dir()) as it:
        for entry in it:
            if entry.is_dir() and os.path.isfile(f"{entry.path}/{CONFIG_FILE}"):
                instances.append(entry.name)
    return instances

def config_dir() -> str:
    path: str = user_config_dir("labbot")
    os.makedirs(path, exist_ok=True)

    return path

def instance_config_dir(name) -> str:
    path = os.path.join(config_dir(), name)

    return path

def write_instance_config(name: str, data: dict) -> None:
    instance_path = instance_config_dir(name)
    os.makedirs(instance_path, exist_ok=True)
    conf_path = os.path.join(instance_path, CONFIG_FILE)

    data = json.loads(json.dumps(data))

    with open(conf_path, "w") as file:
        json.dump(data, file)

    if data != read_instance_config(name):
        raise ValueError("Config could not be saved properly")

def read_instance_config(name: str) -> Dict[str, Any]:
    conf_path = os.path.join(instance_config_dir(name), CONFIG_FILE)

    try:
        with open(conf_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
