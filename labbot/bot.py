import base64
from aiohttp import web
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import logging
import jinja2
import aiohttp_jinja2
from cryptography import fernet
from gidgetlab.aiohttp import GitLabBot
import importlib.resources
from importlib import import_module
import json

from labbot.config import instance_config_dir
from labbot.data import Data

log = logging.getLogger("labbot")

class Bot:

    def __init__(self, *args, name: str, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.name = name
        self.secret = kwargs.get("secret", "")
        self.addons = {}
        self.configs = {}

        self.instance = GitLabBot(name, **kwargs)
        self.instance.app.router.add_get("/dashboard", self.dashboard_handler)
        self.instance.app.router.add_get("/dashboard/login", self.dashboard_login_handler)
        self.instance.app.router.add_post("/dashboard/writer", self.dashboard_writer_handler)

        dashboard_dir = importlib.resources.path("labbot", "dashboard")
        aiohttp_jinja2.setup(
            self.instance.app,
            context_processors=[self.bot_processor],
            loader=jinja2.FileSystemLoader(dashboard_dir)
        )

        addons_dir = importlib.resources.path("labbot", "addons")

        for addon in addons_dir.iterdir():
            if addon.is_file() and addon.name.endswith(".py"):
                self.load_addon(addon.name[:-3])

        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(self.instance.app, EncryptedCookieStorage(secret_key))

    async def bot_processor(self, request) -> dict:
        instance_dir = instance_config_dir(self.name)

        addons = list(self.addons.keys())
        settings = {k:json.dumps(v.read_data(), indent=4) for k, v in self.configs.items()}

        return {
            "bot": {
                "name": self.name,
                "secret": self.secret,
                "addons": addons,
                "instance_dir": instance_dir,
                "settings": settings
            }
        }

    @aiohttp_jinja2.template('index.html')
    async def dashboard_handler(self, request: web.Request) -> dict:
        """Handler to check the health of the bot

        Return 'Bot OK'
        """
        return {}

    @aiohttp_jinja2.template('login.html')
    async def dashboard_login_handler(self, request: web.Request) -> dict:
        """Handler to check the health of the bot

        Return 'Bot OK'
        """
        return {}

    async def dashboard_writer_handler(self, request: web.Request) -> dict:
        """Handler to check the health of the bot

        Return 'Bot OK'
        """
        return "Bot OK"

    def get_data_container(self, *args, **kwargs) -> Data:
        instance_dir = instance_config_dir(self.name)

        container = Data(instance_dir, *args, **kwargs)

        self.configs[args[0]] = container
        return container

    def load_addon(self, addon: str):
        try:
            addon_module = import_module(f"labbot.addons.{addon}")
            addon_module.setup(self)
            self.addons[addon] = addon_module
            log.info(f"Imported {addon}")
        except ModuleNotFoundError:
            log.error(f"Failed to load {addon}")

    def register(self, func, *args, **kwargs):
        return self.instance.router.register(*args, **kwargs)(func)

    def run(self, *args, **kwargs):
        kwargs["print"] = None
        port = kwargs['port']

        log.info(f"Started {self.name} on port {port}")

        self.instance.run(*args, **kwargs)
