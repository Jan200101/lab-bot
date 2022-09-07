"""
a web dashboard for lab-bot
"""
import os
import logging
import json
import time
from functools import wraps

import aiohttp
import jinja2
import aiohttp_jinja2 # type: ignore
from itsdangerous.url_safe import URLSafeSerializer
from itsdangerous.exc import BadSignature

from labbot import __version__ as labbot_version
from labbot.config import Config

log = logging.getLogger(__name__)

config = Config(__name__)
config.set_global_data(
    accounts={
        "admin":"admin"
    },
    secret="secret",
    salt="salt123"
)

class BufferHandler(logging.Handler):
    def __init__(self, lines=-1):
        super().__init__(level=logging.DEBUG)
        self.log_buffer = []
        self.lines = lines

    def emit(self, record):

        try:
            msg = self.format(record)
            return self.log_buffer.append(msg)
        finally:
            if self.lines > 0:
                while len(self.log_buffer) > self.lines:
                    self.log_buffer.remove(0)

auth_s = URLSafeSerializer(config["secret"], config["salt"])
def check_auth():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            full_kwargs = kwargs.copy()
            full_kwargs.update(zip(func.__code__.co_varnames, args))
            try:
                request = full_kwargs["coro"]
            except KeyError:
                try:
                    request = full_kwargs["args"]
                except KeyError:
                    request = full_kwargs["request"]

            try:
                session = request.cookies["session"]
                data = auth_s.loads(session)
                return await func(*args, **kwargs)
            except (KeyError, BadSignature):
                resp = aiohttp.web.HTTPFound(
                    location='/login',
                    headers=request.headers
                )
                resp.del_cookie("session")
                raise resp 


        return wrapper
    return decorator

def set_auth():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            full_kwargs = kwargs.copy()
            full_kwargs.update(zip(func.__code__.co_varnames, args))
            try:
                request = full_kwargs["coro"]
            except KeyError:
                try:
                    request = full_kwargs["args"]
                except KeyError:
                    request = full_kwargs["request"]

            if request.method == "POST":
                data = await request.post()
                try:
                    username = data["username"]
                    password = data["password"]
                    if config["accounts"].get(username, "") == password:
                        resp = aiohttp.web.HTTPFound(
                            location='/',
                            headers=request.headers
                        )
                        resp.set_cookie("session", auth_s.dumps({"time": time.time(), "username": username}), max_age=300)
                        raise resp
                except KeyError:
                    pass
            return await func(*args, **kwargs)

        return wrapper
    return decorator

class Dashboard:

    def __init__(self, bot):
        self.bot = bot
        self.app = self.bot.instance.app

        formatter = logging.Formatter(
            "[{asctime}] [{levelname}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{"
        )

        self.buffer_handler = BufferHandler()
        self.buffer_handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(self.buffer_handler)
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
        ]

        for addon in self.bot.addons:
            self.pages.append([f"/settings/{addon}", self.addon_settings(addon)])

        for page in self.pages:
            endpoint, func = page
            self.app.router.add_get(endpoint, func)
        self.app.router.add_get("/login", self.login)
        self.app.router.add_post("/login", self.login)
        self.app.router.add_get("/logout", self.logout)

    @check_auth()
    @aiohttp_jinja2.template('index.html')
    async def dashboard(self, request: aiohttp.web.Request) -> dict:
        return {}

    @check_auth()
    @aiohttp_jinja2.template('log.html')
    async def log(self, request: aiohttp.web.Request) -> dict:
        return {}

    @check_auth()
    @aiohttp_jinja2.template('settings.html')
    async def settings(self, request: aiohttp.web.Request) -> dict:
        return {}

    def addon_settings(self, addon):
        @check_auth()
        @aiohttp_jinja2.template('addon_settings.html')
        async def _settings(request: aiohttp.web.Request) -> dict:
            c = Config(addon, self.bot.name)
            return {
                "addon_settings": c.settings
            }

        return _settings

    @set_auth()
    @aiohttp_jinja2.template('login.html')
    async def login(self, request: aiohttp.web.Request) -> dict:
        return {}

    @check_auth()
    async def logout(self, request: aiohttp.web.Request):
        resp = aiohttp.web.HTTPFound(
            location='/login',
            headers=request.headers
        )
        resp.del_cookie("session")
        return resp 

    async def processor(self, request) -> dict:
        return {
            "bot": {
                "name": self.bot.name,
                "version": labbot_version,
                "addons": self.bot.addons,
                "config": self.bot.config,

                "log": "\n".join(self.buffer_handler.log_buffer)
            }
        }

    async def event_processor(self, *args, **kwargs):
        self.event_counter += 1

def setup(bot):
    config.setup(__name__, bot.name)
    config.save()
    Dashboard(bot)
