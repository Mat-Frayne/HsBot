#!/usr/bin/env python
"""."""
import asyncio
import sys
import time
import traceback

import discord
import plugins
from cogs.utils import misc
from discord.errors import LoginFailure
from discord.ext import commands
#  from threading import Thread
# from plugins import app


db = plugins.database
description = """
Hello! I am a bot written by Subarashii based off of RoboDanny.py,
mee6.py and discord.py
"""
help_attrs = dict(hidden=True)


class Bot(commands.Bot):
    """."""

    def __init_(self, **options):
        """."""
        super().__init__(**options)
        self.initial_extensions = [
            'cogs.general',
            'cogs.admin',
            'cogs.hearthstone',
        ]

    @asyncio.coroutine
    def _get_prefix(self, message):
        prefix = db.table_data(
            "ServerPrefixes", "ServerId", message.server.id)[0]["Prefix"]
        # self.command_prefix
        if callable(prefix):
            ret = prefix(self, message)
            if asyncio.iscoroutine(ret):
                ret = yield from ret
            return ret
        else:
            return prefix

bot = Bot(command_prefix=['!', '?', '\u2757'],
          description=description, pm_help=None,
          help_attrs=help_attrs)
setattr(bot, 'database', db)
setattr(bot, 'errdb', plugins.errordb)
setattr(bot, 'url', "localhost")
setattr(bot, 'img_url', "139.59.234.223")

@bot.event
@asyncio.coroutine
def on_ready():
    """On-ready event for discord bot."""
    print('------------------------------------')
    print('Logged in as:')
    print('Username: ' + bot.user.name)
    print('ID: ' + bot.user.id)
    print('------------------------------------')
    if not hasattr(bot, 'uptime'):
        bot.starttime = time.time()
    dbservers = [x["ServerId"] for x in db.table_data("ServerPrefixes")]
    for server in bot.servers:
        if server.id not in dbservers:
            db.insert_row(
                "ServerPrefixes",
                {"ServerId": server.id, "Prefix": "!",
                 "InTextWraps": "{}"},
                raise_integ="hide")


@bot.event
@asyncio.coroutine
def on_message(message):
    """."""
    if message.author.bot:
        return
    # g = db.table_data("ChannelPrefixes", "ChannelID", message.server.id)
    # check = g[0]["Prefix"] if len(g) > 0 else None

    # if check and check == message.content[0]:
    #     message.content = "!" + message.content[1:]
    yield from bot.process_commands(message)


@bot.event
async def on_command_error(error, ctx):
    """."""
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(
            ctx.message.author,
            'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(
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


def setup_logins():
    """Setup function for api's."""
    datas = ["Token", "Secret", "Client_Id"]

    for data in datas:
        d = db.table_data("Client", "Data", data)[0]['Value'] if\
            len(db.table_data("Client", "Data", data)) > 0 else None
        while not d:
            di = input("\tYour {}: ".format(data.lower()))
            if di:
                db.change_data("Client", {"Value": di}, {"Data": data})
            d = db.table_data("Client", "Data", data)[0]['Value'] if\
                len(db.table_data("Client", "Data", data)) > 0 else None


async def hs_updater():
    """."""
    while 1:
        k = db.table_data("Client", "Data", "Hs_json_last")
        last_run = k[0]["Value"] if len(k) > 0 else 0
        if float(last_run) + 14400 < time.time():  # 4 hours
            cards = yield from misc.get(misc.hsCards)
            backs = yield from misc.get(misc.hsBacks)
            colllectables = yield from misc.get(misc.hsCollectable)
            hs = {"cards": {}, "backs": {}, "collectables": {}}
            hs["cards"] = cards
            hs["backs"] = backs
            hs["collectables"] = colllectables
            setattr(bot, "hs", hs)
            yield from bot.change_presence(
                game=discord.Game(name="Online!"))
            db.change_data(
                "Client", {"Value": str(time.time())},
                {"Data": "Hs_json_last"})
            print("Hearthstone Updated!")
        yield from asyncio.sleep(14400)

if __name__ == '__main__':
    def start():
        """."""
        while 1:
            try:

                setup_logins()
                # loop = asyncio.get_event_loop()
                # t = Thread(target=app_main, args=(loop,),
                #  name="MainBotThread")
                # t.start()
                for extension in bot.initial_extensions:
                    try:
                        bot.load_extension(extension)
                    except Exception as e:
                        print('Failed to load extension {}\n{}: {}'
                              .format(extension, type(e).__name__, e))
                bot.loop.create_task(hs_updater())
                bot.run(db.table_data("Client", "Data", "Token")[0]['Value'])
            except LoginFailure:
                print("Error Loggin in! Invalid Token, reseting Token.....")
                db.change_data("Client", {"Value": ""}, {"Data": "Token"})
                setup_logins()
                start()
            except Exception as e:
                print(e)
                break
    start()
