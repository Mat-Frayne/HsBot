#!/usr/bin/env python
"""."""
import asyncio
import configparser
import logging
from time import time
import traceback
import sys
import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.exc import IntegrityError

from database.models import Model

CONFIG = configparser.ConfigParser()
with open('settings.ini', "r") as f:
    CONFIG.read_file(f)

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


class Client(commands.Bot):
    """."""

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.starttime = time()
        self.engine = create_engine("sqlite:///database/main.db")
        self.conn = self.engine.connect()
        self.models = Model(self.engine)
        if kwargs.get("ow"):
            self.loop.create_task(kwargs.get("ow"))

    async def on_ready(self):
        """."""
        await self.change_presence(status=discord.Status.do_not_disturb, afk=True)
        print('Logged in as', self.user, "\n----------------------")
        try:
            self.conn.execute(self.models.stats.insert(), [
                {'Stat': 'Commands_used', 'Value': 0},
                {'Stat': 'Messages_recieved', 'Value': 0},
             {'Stat': 'Messages_sent', 'Value': 0}
            ])
        except IntegrityError:
            pass
        await self.wait_until_ready()
        await asyncio.sleep(10)

    async def on_message(self, message):
        """."""
        if message.author.id == self.user.id:
            return
        stats = self.models.stats
        statement = select([stats]).where(stats.c.Stat == "Messages_recieved")
        query = self.conn.execute(statement).first()
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
                ret = await ret
            return ret
        else:
            return prefix

    async def on_command(self, ctx):
        """."""
        # print(dir(ctx))
        pass

    def on_command_error(self, ctx, error):
        """."""
        if isinstance(error, commands.NoPrivateMessage):
            yield from ctx.send_message(
                ctx.message.author,
                'This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            yield from ctx.send_message(
                ctx.message.author,
                'Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            # if error.original.__class__.__name__ == "AttributeError":
            #     yield from bot.send_message(
            #         ctx.message.channel,
            #         "Command cannot be used in Private channel.")
            #     return
            print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print('{0.__class__.__name__}: {0}'.format(
                error.original), file=sys.stderr)
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            traceback.print_tb(error)


BOT = Client(command_prefix='!')

if __name__ == '__main__':
    BOT.load_extension("cogs.Admin")
    BOT.run(CONFIG.get("tokens", "subatest"))
