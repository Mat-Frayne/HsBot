"""General cog for Heartshone bot."""
from discord.ext import commands
import asyncio
import discord


class General:
    """."""

    def __init__(self, bot):
        """."""
        self.bot = bot

    @commands.command()
    @asyncio.coroutine
    def invite(self):
        """Get the bots invite link."""
        url = ("https://discordapp.com/oauth2/authorize?client_id=" +
               self.bot.database.table_data(
                   "Client", "Data", "Client_Id")[0]['Value'] +
               "&scope=bot&permissions=000008")
        yield from self.bot.say(url)

    @commands.command(pass_context=True)
    @asyncio.coroutine
    def prefix(self, ctx, *, prefix: str = ""):
        """Get or change the bots prefix for this server."""
        pass

    @commands.command(pass_context=True)
    @asyncio.coroutine
    def wraps(self, ctx, *, wraps: str = ""):
        """Get, change or remove the bots in-text-wraps for this server."""
        pass

    @asyncio.coroutine
    def on_server_join(self, server):
        """Excecute when bot joins server."""
        dbservers = [x["ChannelID"] for x in self.bot.database.table_data(
            "ChannelPrefixes")]
        if server.id not in dbservers:
            self.bot.database.insert_row(
                "ChannelPrefixes",
                {"ChannelID": server.id, "Prefix": "!",
                 "InTextWraps": "{}"},
                raise_integ="hide")

    @asyncio.coroutine
    def on_server_leave(self, server):
        """Excecute when bot joins server."""
        self.bot.database.remove_column(
            "ChannelPrefixes", {"ChannelID": server.id})

    @commands.command(pass_context=True)
    @asyncio.coroutine
    def test(self, ctx):
        """."""
        embed = discord.Embed(description='Classic')
        embed.title = '**Frothing Berserker**'
        embed.url = 'http://wow.zamimg.com/images/hearthstone/cards/enus/original/EX1_604.png'
        embed.set_image(url="http://wow.zamimg.com/images/hearthstone/cards/enus/original/EX1_604.png")
        embed.add_field(name='Arena value:', value="71 (avg)")

        yield from self.bot.say(embed=embed)


def setup(bot):
    """."""
    bot.add_cog(General(bot))
