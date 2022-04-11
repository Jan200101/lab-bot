import base64
from aiohttp import web
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import jinja2
import aiohttp_jinja2
from cryptography import fernet
from gidgetlab.aiohttp import GitLabBot
import importlib.resources

class Bot:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.instance = GitLabBot("lab-bot", **kwargs)
        self.instance.app.router.add_get("/dashboard", self.dashboard_handler)

        dashboard_files = importlib.resources.path("labbot", "dashboard")

        aiohttp_jinja2.setup(self.instance.app, loader=jinja2.FileSystemLoader(dashboard_files))

        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(self.instance.app, EncryptedCookieStorage(secret_key))


    @aiohttp_jinja2.template('login.html')
    async def dashboard_handler(self, request: web.Request) -> dict:
        """Handler to check the health of the bot

        Return 'Bot OK'
        """
        return {}

    def register(self, func, *args, **kwargs):
        return self.instance.router.register(*args, **kwargs)(func)

    def run(self, *args, **kwargs):
        self.instance.run(*args, **kwargs)