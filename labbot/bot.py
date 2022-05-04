import os.path
import sys
from gidgetlab.aiohttp import GitLabBot
from importlib import import_module
import logging

import labbot
import labbot.config

log = logging.getLogger(__name__)

class Bot:

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name", "lab-bot")
        self.secret = kwargs.get("secret", "")
        self.config = kwargs.get("config", labbot.config.read_instance_config(self.name))

        self.addons = self.config.get("addons", [])
        self.addon_paths = []

        self.core_addon_path = os.path.join(os.path.dirname(labbot.__file__), "addons")
        self.addon_paths.append(self.core_addon_path)
        if "addon_path" in self.config:
            self.addon_paths.append(self.config.get("addon_path"))

        self.instance = GitLabBot(self.name, **kwargs)

        for path in self.addon_paths:
            sys.path.insert(0, path)

        for addon in self.addons:
            self.load_addon(addon)

        for path in self.addon_paths:
            sys.path.remove(path)


    def load_addon(self, addon: str):
        try:
            import_module(f"{addon}").setup(self)
            log.info(f"Loaded {addon}")
        except ModuleNotFoundError:
            log.error(f"No addon named `{addon}`")

    def register(self, func, *args, **kwargs):
        return self.instance.router.register(*args, **kwargs)(func)

    def run(self, *args, **kwargs):
        log.info(f"Started {self.name}")
        self.instance.run(*args, **kwargs)