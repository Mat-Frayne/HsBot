#!/usr/bin/env python
"""."""
import asyncio
import configparser
from time import time

import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.sql import select

from database.models import Model

CONFIG = configparser.ConfigParser()
with open('settings.ini', "r") as f:
    CONFIG.read_file(f)


class Client(commands.Bot):
    """."""

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.starttime = time()
        self.engine = create_engine("sqlite:///database/main.db", echo=True)
        self.conn = self.engine.connect()

        self.models = Model(self.engine)
        if kwargs.get("ow"):
            self.loop.create_task(kwargs.get("ow"))

    async def on_ready(self):
        """."""
        await self.change_presence(status=discord.Status.do_not_disturb, afk=True)
        print('Logged in as', self.user, "\n----------------------")
        self.conn.execute(self.models.stats.insert(), [
            {'Stat': 'Commands_used', 'Value': 0},
            {'Stat': 'Messages_recieved', 'Value': 0},
            {'Stat': 'Messages_sent', 'Value': 0}
        ])
        await self.wait_until_ready()
        await asyncio.sleep(10)
        await self.change_presence(status=discord.Status.invisible)

    async def on_message(self, message):
        """."""
        if message.author.id == self.user.id:
            return
        stats = self.models.stats
        statement = select([stats]).where(stats.c.Stat == "Messages_recieved")
        query = self.conn.execute(statement).first()
        print(query["Value"])
        smtm = stats.update().where(stats.c.Stat == "Messages_recieved").values(
            Value=query["Value"] + 1)
        self.conn.execute(smtm)
        await self.process_commands(message)

    async def get_prefix(self, message):
        """|coro|
        Retrieves the prefix the bot is listening to
        with the message as a context.
        Parameters
        -----------
        message: :class:`discord.Message`
            The message context to get the prefix of.
        Returns
        --------
        Union[List[str], str]
            A list of prefixes or a single prefix that the bot is
            listening for.
        """
        prefix = self.command_prefix
        if callable(prefix):
            ret = prefix(self, message)
            if asyncio.iscoroutine(ret):
                ret = yield from ret
            return ret
        else:
            return prefix

BOT = Client(command_prefix='!')

MODULES = []

if __name__ == '__main__':
    for x in MODULES:
        BOT.load_extension('cogs.' + x)
    BOT.run(CONFIG.get("tokens", "subatest"))
