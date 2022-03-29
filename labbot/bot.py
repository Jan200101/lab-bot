from gidgetlab.aiohttp import GitLabBot

class Bot:

    def __init__(self, *args, **kwargs):
        self.instance = GitLabBot("lab-bot", **kwargs)
        pass

    def register(self, func, *args, **kwargs):
        return self.instance.router.register(*args, **kwargs)(func)

    def run(self, *args, **kwargs):
        self.instance.run(*args, **kwargs)