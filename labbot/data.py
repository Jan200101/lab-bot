import os.path
import json
from typing import Dict, Any

from labbot.config import instance_config_dir

class Data:

    def __init__(self, instance_dir: str, addon_id: str, default_dict: Dict[str, Any]):
        self.instance_dir = instance_dir
        self.addon_id = addon_id
        self.default_dict = default_dict
        
        self.path = os.path.join(self.instance_dir, self.addon_id+".json")

    def read_data(self) -> Dict[str, Any]:
        retval = self.default_dict.copy()
        try:
            with open(self.path, "r") as fd:
                retval.update(json.load(fd))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

        return retval

    def write_data(self, data: Dict[str, Any]):
        dump = {}
        for key in data.keys():
            if (not key in self.default_dict
                or data[key] != self.default_dict[key]):
                dump[key] = data[key]

        with open(self.path, "w") as fd:
            json.dump(dump, fd)
