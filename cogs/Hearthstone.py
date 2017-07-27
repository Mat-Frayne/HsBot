#!/usr/bin/env python
"""."""
from time import time

import aiohttp
from discord.ext import commands

from .utils import misc


class Hearthstone:
    """."""

    def __init__(self, bot):
        """."""
        self.bot = bot
        self.data = None
        self.lastupdated = None

    @commands.command(aliases=["hs", "HS"])
    async def hearthstone(self, ctx, *, query: str):
        """."""
        await self.update()
        await ctx.send("`sadfasdf` {}".format(query))

    async def update(self):
        """."""
        if not self.lastupdated or (time() - self.lastupdated) > 3600:
            async with aiohttp.ClientSession() as clientsession:
                async with clientsession.get(misc.DATA.get("hsCollectable")) as resp:
                    if 199 < resp.status < 300:
                        res = await resp.json()
                        self.data = res
                        self.lastupdated = time()
                        return True
                    return False



def setup(bot):
    """."""
    bot.add_cog(Hearthstone(bot))
