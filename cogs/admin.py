"""."""
from discord.ext import commands
import asyncio
from .utils import checks
import sys


class Admin:
    """."""

    def __init__(self, bot):
        """."""
        self.bot = bot

    @commands.command(name='reload', aliases=["r"], hidden=True)
    @checks.is_owner()
    @asyncio.coroutine
    def _reload(self, *, module: str):
        """Reload a module."""
        out = ""
        if "all" in module.lower():
            for x in self.bot.initial_extensions:
                try:
                    self.bot.unload_extension(x)
                    self.bot.load_extension(x)
                    out = "{}\nReloaded {}".format(out, x)
                except Exception as e:
                    out = "{}\nFailed to reload {}\n\t{}: {}"\
                        .format(out, x, type(e).__name__, e)
        else:
            try:

                self.bot.unload_extension(module)
                self.bot.load_extension(module)
                out = "Reloaded {}".format(module)
            except Exception as e:
                out = '{}: {}'.format(type(e).__name__, e)
        yield from self.bot.say(out)

    @commands.group(name="force")
    @checks.is_owner()
    @asyncio.coroutine
    def _force(self):
        """."""
        pass

    @_force.command(name='stop', aliases=[], hidden=True)
    @checks.is_owner()
    @asyncio.coroutine
    def _force_exit(self):
        """."""
        yield from self.bot.say("Stopping Bot. :cry: :gun:")
        sys.exit("Forced stop.")

    @commands.command(name="dbping", hidden=True)
    @checks.is_owner()
    @asyncio.coroutine
    def t(self):
        """."""
        top = 0
        lowest = 0
        self.bot.database.table


def setup(bot):
    """."""
    bot.add_cog(Admin(bot))
