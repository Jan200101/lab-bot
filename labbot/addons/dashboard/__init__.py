"""
a web dashboard for lab-bot
"""
import os
import logging

import aiohttp
import jinja2
import aiohttp_jinja2 # type: ignore

log = logging.getLogger(__name__)

class Dashboard:

    def __init__(self, bot):
        self.bot = bot
        self.app = self.bot.instance.app

        dashboard_dir = os.path.join(os.path.dirname(__file__), "templates")
        aiohttp_jinja2.setup(
            self.app,
            context_processors=[self.processor],
            loader=jinja2.FileSystemLoader(dashboard_dir))

        self.app.router.add_get("/dashboard", self.index)
        log.info("Running dashboard under /dashboard")

        self.bot.register_merge_hook(self.merge_hook)
        self.bot.register_issue_hook(self.issue_hook)
        self.bot.register_push_hook(self.push_hook)

        self.event_count = 0

    @aiohttp_jinja2.template('index.html')
    async def index(self, request: aiohttp.web.Request) -> dict:
        """Handler to check the health of the bot

        Return 'Bot OK'
        """
        return {}

    async def processor(self, request) -> dict:
        return {
            "bot": {
                "name": self.bot.name,
                "addons": self.bot.addons,

                "event_count": self.event_count
            }
        }

    async def merge_hook(self, *args, **kwargs):
        print("test")
        self.event_count += 1
        pass

    async def issue_hook(self, *args, **kwargs):
        self.event_count += 1
        pass

    async def push_hook(self, *args, **kwargs):
        self.event_count += 1
        pass

def setup(bot):
    Dashboard(bot)
