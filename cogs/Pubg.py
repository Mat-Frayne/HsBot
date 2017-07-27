"""."""
import time
import discord
from discord.ext import commands
from pypubg import core
from .utils import misc


class Pubg:
    """."""

    def __init__(self, bot):
        """."""
        self.bot = bot
        self.api = core.PUBGAPI(self.bot.config.get("api", "pubg"))

    @commands.group(name="pubg", invoke_without_command=True)
    async def _pubg(self, ctx):
        pass

    @_pubg.command(name="stats", hidden=True)
    async def _stats(self, ctx, name: str, mode_: str = ""):
        """."""

        if mode_.strip().lower() not in ["solo", "duo", "squad"]:
            await ctx.send("No mode given!, use {}pubg stats {} `<solo, duo or squad>`"
                           .format(await self.bot.get_prefix(
                               ctx.message), name.strip()))
            return
        stats = self.api.player(name.strip())
        if stats.get("error"):
            await ctx.send("Error from api server:\n```{}```".format(stats.get("message")))
            return
        if len(stats.get("Stats", [])) < 1:
            await ctx.send("Error collecting stats for: {}".format(name))
            print(stats)
            return

        modes = {}
        for mode in stats.get("Stats"):
            if mode.get("Region") == "oc":
                modes[mode.get("Match")] = mode
        if not modes.get(mode_.lower()):
            await ctx.send("Error fetching data for {}.".format(mode_.lower()))

        embed = discord.Embed(title="Region: OC",
                              colour=discord.Colour(0x443f2))
        embed.set_thumbnail(
            url="https://pbs.twimg.com/profile_images/838644954272428032/cFpoFSZA.jpg")
        embed.set_author(name="{}:{}".format(stats.get("PlayerName"), stats.get("PubgTrackerId")),
                         url="https://pubgtracker.com/profile/pc/subarashii_",
                         icon_url=stats.get("Avatar", None))
        out = []
        for section in modes.get(mode_.strip().lower()).get("Stats"):
            out.append("**{}:**  {}\n".format(section.get(
                "label", "NA"), section.get("value")))

        def split_(list_, range_):
            """."""
            king, mobs = divmod(len(list_), range_)
            return (list_[i * king + min(i, mobs):(
                i + 1) * king + min(i + 1, mobs)] for i in range(range_))
        lines = list(split_(out, 4))

        for line in lines:
            embed.add_field(name="\u200B", value="".join(line))
        rating = self.api.player_skill(
            name.strip(), game_mode=mode_.strip().lower())
        if rating:
            out = ""
            for server in rating:
                out = out + \
                    "**{}:**  {}\n".format(server, rating.get(server))
            embed.add_field(name="Skill Rating",
                            value=out, inline=False)
        last = stats.get("LastUpdated")

        mytime = last[:-1].split("T")

        old = time.strptime("{} {}".format(
            mytime[0], mytime[1].split(".")[0]), '%Y-%m-%d %H:%M:%S')
        new = time.gmtime()
        seconds = new.tm_sec - old.tm_sec
        seconds += (new.tm_min - old.tm_min) * 60
        seconds += (new.tm_hour - old.tm_hour) * 60 * 60
        seconds += (new.tm_mday - old.tm_mday) * 60 * 60 * 24
        times_ = await misc.diffrence(0, seconds)
        embed.set_footer(text="Last Updated: {} ({} ago)".format(
            time.strftime('%d-%m-%Y %I:%M:%S%p UTC', old), times_))
        await ctx.send(embed=embed)


    @_pubg.command()
    async def squad(self, ctx, *, query: str):
        """."""
        await ctx.invoke(self._stats, name=query, mode_="squad")

    @_pubg.command()
    async def duo(self, ctx, *, query: str):
        """."""
        await ctx.invoke(self._stats, name=query, mode_="duo")
    
    
    @_pubg.command()
    async def solo(self, ctx, *, query: str):
        """."""
        await ctx.invoke(self._stats, name=query, mode_="solo")

def setup(bot):
    """."""
    bot.add_cog(Pubg(bot))
