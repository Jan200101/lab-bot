"""
a web dashboard for lab-bot
"""
import os
import logging
import json

import aiohttp
import jinja2
import aiohttp_jinja2 # type: ignore

from labbot import __version__ as labbot_version
from labbot.config import Config

log = logging.getLogger(__name__)

class BufferHandler(logging.Handler):
    def __init__(self, dashboard, lines=-1):
        super().__init__(level=logging.DEBUG)
        self.dashboard = dashboard
        self.lines = lines

    def emit(self, record):

        try:
            msg = self.format(record)
            return self.dashboard.log_buffer.append(msg)
        finally:
            if self.lines > 0:
                while len(self.dashboard.log_buffer) > self.lines:
                    self.dashboard.log_buffer.remove(0)

class Dashboard:

    def __init__(self, bot):
        self.bot = bot
        self.app = self.bot.instance.app
        self.log_buffer = []

        formatter = logging.Formatter(
            "[{asctime}] [{levelname}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{"
        )

        buffer_handler = BufferHandler(self)
        buffer_handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(buffer_handler)
        del root_logger

        dashboard_dir = os.path.join(os.path.dirname(__file__), "templates")
        aiohttp_jinja2.setup(
            self.app,
            context_processors=[self.processor],
            loader=jinja2.FileSystemLoader(dashboard_dir))

        self.pages = [
            ["/",           self.dashboard],
            ["/log",        self.log],
            ["/settings",   self.settings],
            ["/settings/dashboard", self.addon_settings("dashboard")],
        ]

        for addon in self.bot.addons:
            self.pages.append([f"/settings/{addon}", self.addon_settings(addon)])

        for page in self.pages:
            endpoint, func = page
            self.app.router.add_get(endpoint, func)

    @aiohttp_jinja2.template('index.html')
    async def dashboard(self, request: aiohttp.web.Request) -> dict:
        return {}

    @aiohttp_jinja2.template('log.html')
    async def log(self, request: aiohttp.web.Request) -> dict:
        return {}

    @aiohttp_jinja2.template('settings.html')
    async def settings(self, request: aiohttp.web.Request) -> dict:
        return {}

    def addon_settings(self, addon):

        @aiohttp_jinja2.template('addon_settings.html')
        async def _settings(request: aiohttp.web.Request) -> dict:
            c = Config(addon, self.bot.name)
            return {
                "addon_settings": c.settings
            }

        return _settings

    async def processor(self, request) -> dict:
        return {
            "bot": {
                "name": self.bot.name,
                "version": labbot_version,
                "addons": self.bot.addons,
                "config": self.bot.config,

                "log": "\n".join(self.log_buffer)
            }
        }

    async def event_processor(self, *args, **kwargs):
        self.event_counter += 1

def setup(bot):
    Dashboard(bot)
