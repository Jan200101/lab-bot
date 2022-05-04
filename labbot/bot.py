import os.path
import sys
from gidgetlab.aiohttp import GitLabBot # type: ignore
from importlib import import_module
import logging

import labbot
import labbot.config

log = logging.getLogger(__name__)

class Bot:

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop("name", "lab-bot")
        self.access_token = kwargs.get("access_token")
        self.secret = kwargs.get("secret", "")
        self.config = kwargs.pop("config", labbot.config.read_instance_config(self.name))
        self.config_addons = self.config.get("addons", [])

        self.addons = []
        self.addon_paths = []

        self.core_addon_path = os.path.join(os.path.dirname(labbot.__file__), "addons")
        self.addon_paths.append(self.core_addon_path)
        if "addon_path" in self.config:
            self.addon_paths.append(self.config.get("addon_path"))

        self.instance = GitLabBot(self.name, **kwargs)

        for path in self.addon_paths:
            sys.path.insert(0, path)

        for addon in self.config_addons:
            self.load_addon(addon)

        for path in self.addon_paths:
            sys.path.remove(path)


    def load_addon(self, addon: str) -> None:
        try:
            import_module(f"{addon}").setup(self)
            log.info(f"Loaded {addon}")
            self.addons.append(addon)
        except ModuleNotFoundError:
            log.error(f"No addon named `{addon}`")
        except Exception as e:
            log.exception(e)

    def register(self, func, *args, **kwargs) -> None:
        self.instance.router.register(*args, **kwargs)(func)

    def register_push_hook(self, func, *args, **kwargs) -> None:
        self.register(func, "Push Hook", *args, **kwargs)

    def register_tag_hook(self, func, *args, **kwargs) -> None:
        self.register(func, "Tag Push Hook", *args, **kwargs)

    def register_issue_hook(self, func, *args, **kwargs) -> None:
        self.register(func, "Issue Hook", *args, **kwargs)

    def register_note_hook(self, func, *args, **kwargs) -> None:
        self.register(func, "Note Hook", *args, **kwargs)

    def register_merge_hook(self, func, *args, **kwargs) -> None:
        self.register(func, "Merge Request Hook", *args, **kwargs)

    def register_wiki_hook(self, func, *args, **kwargs) -> None:
        self.register(func, "Wiki Page Hook", *args, **kwargs)

    def register_pipeline_hook(self, func, *args, **kwargs) -> None:
        self.register(func, "Pipeline Hook", *args, **kwargs)

    def register_job_hook(self, func, *args, **kwargs) -> None:
        self.register(func, "Job Hook", *args, **kwargs)

    def register_deployment_hook(self, func, *args, **kwargs) -> None:
        self.register(func, "Deployment Hook", *args, **kwargs)


    def run(self, *args, **kwargs) -> None:
        log.info(f"Started {self.name}")
        self.instance.run(*args, print=False, **kwargs)