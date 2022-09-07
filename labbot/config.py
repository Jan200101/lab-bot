import os
import json
from typing import List, Dict, Any
from appdirs import user_config_dir  # type: ignore
from functools import wraps

CONFIG_FILE = "config.json"

class Config:
    def __init__(self, conf_name=None, name=None):
        self.conf_name = conf_name
        self.name = name

        self.settings = {
            "GLOBAL": {},
            "GROUP": {},
            "PROJECT": {},
        }
        self.group_id = None
        self.project_id = None

        if self.conf_name and self.name:
            self.setup(self.conf_name, self.name)

    def setup(self, conf_name, name):
        instance_path = instance_config_dir(name)
        if conf_name.endswith(".json"):
            conf_name = conf_name[:-5]

        if conf_name == "config":
            raise ValueError("Config cannot be named config")

        self.conf_name = conf_name
        self.name = name

        try:
            global_data = self.settings.get("GLOBAL", {})

            self.settings = json.load(
                open(os.path.join(instance_path, f"{conf_name}.json")))

            # write the hardcoded config data ontop of the loaded data
            self.settings["GLOBAL"].update(global_data)

            try:
                self.settings["PROJECT"] = self.settings.pop("REPO")
            except KeyError:
                pass
        except (IOError, ValueError):
            pass

    def __getitem__(self, key):
        try:
            return self.settings["PROJECT"][str(self.project_id)][key]
        except KeyError:
            try:
                return self.settings["GROUP"][str(self.group_id)][key]
            except KeyError:
                return self.settings["GLOBAL"][key]

    def save(self):
        instance_path = instance_config_dir(self.name)
        conf_path = os.path.join(instance_path, f"{self.conf_name}.json")

        with open(conf_path, "w") as f:
            json.dump(self.settings, f)

    def config_decorator(self, **dkwargs):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):

                full_kwargs = kwargs.copy()
                full_kwargs.update(zip(func.__code__.co_varnames, args))
                try:
                    event = full_kwargs["event"]
                    self.project_id = event.project_id
                except KeyError:
                    pass

                try:
                    return await func(*args, **kwargs)
                finally:
                    self.group_id = None
                    self.project_id = None
                    self.save()

            return wrapper
        return decorator

    def set_global_data(self, **kwargs):
        self.settings["GLOBAL"] = kwargs

    def set_group_data(self, group_id, **kwargs):
        self.settings["GROUP"][group_id] = kwargs

    def set_project_data(self, project_id, **kwargs):
        self.settings["PROJECT"][project_id] = kwargs

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
