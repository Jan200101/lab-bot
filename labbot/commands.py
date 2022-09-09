"""
Command Framework for Lab-Bot
Allows the creation of functions that run when specific comments are made
e.g.
!close -> closes issue
"""

import logging

log = logging.getLogger(__name__)

class Commands:

    def __init__(self, **kwargs):
        self.prefix = kwargs.get("prefix", "!")
        self.hooks = {}

    def command(self, *args, name=None, aliases=None):
        def decorator(func):
            nonlocal name
            nonlocal aliases

            if name is None:
                name = func.__name__

            if aliases is None:
                aliases = []

            aliases.append(name)

            for alias in aliases:
                self.hooks[alias] = func

        return decorator

    async def process_note(self, event, gl, *args, **kwargs):
        note = event.object_attributes.get("note", "").strip()
        if not note.startswith(self.prefix):
            return

        note = note[len(self.prefix):]

        note = note.split()
        command = note[0]
        arguments = note[1:]

        hook = None
        try:
            hook = self.hooks[command]
        except KeyError:
            log.warn(f"Attempted to invoke nonexistant command `{command}`")

        if hook:
            await hook(event, gl, *arguments)
    def setup_hook(self, bot):
        bot.register_note_hook(self.process_note)

commands = Commands()
