"""."""
import os
import aiohttp
from discord import Embed, File
from discord.ext import commands

from PIL import Image, ImageDraw, ImageFont


class Runescape:
    """."""

    def __init__(self, bot):
        """."""
        self.bot = bot

    @commands.command()
    async def stats(self, ctx, *, name: str):
        """."""
        uni1 = "⚫"
        uni2 = "⚪"

        desc = str(uni1 * 1 + uni2 * 9)
        embed = Embed(title="10%", description=desc,
                      colour=0xDEADBF)
        dembed = await ctx.send(embed=embed)

        async def get(name):
            """."""
            async with aiohttp.ClientSession() as clientsess:
                async with clientsess.get(
                    'http://services.runescape.com/m=hiscore' +
                    '_oldschool/index_lite.ws?player=' + name) as resp:

                    if not resp.status == 200:
                        # await ctx.send("```{}: No player {} Found```".format(resp.status, name))
                        return False
                    return await resp.text()
        json_ = await get(name)
        if not json_:
            embed = Embed(title="```404: No player {} Found```".format(name), description="\u200D",
                          colour=0xff0000)
            await dembed.edit(embed=embed)
            return

        desc = str(uni1 * 2 + uni2 * 8)
        embed = Embed(title="20%", description=desc,
                      colour=0xDEADBF)
        await dembed.edit(embed=embed)

        img = Image.open("cogs/utils/RunescapeStats.png")
        draw = ImageDraw.Draw(img)

        desc = str(uni1 * 3 + uni2 * 7)
        embed = Embed(title="30%", description=desc,
                      colour=0xDEADBF)
        await dembed.edit(embed=embed)

        font = ImageFont.truetype("fonts/runescape_friends_list.ttf", 16)
        parts = json_.replace(" ", ",").split(",")[1::2][:24]
        rows = (57, 122, 186)
        skills = {}

        desc = str(uni1 * 4 + uni2 * 6)
        embed = Embed(title="40%", description=desc,
                      colour=0xDEADBF)
        await dembed.edit(embed=embed)

        skills["Overall"] = (185 - ((len(parts[0]) / 2) * 6), 277)
        skills["Attack"] = (rows[0], 50)
        skills["Defence"] = (rows[0], 112)
        skills["Strength"] = (rows[0], 81)
        skills["Hitpoints"] = (rows[1], 50)
        skills["Ranged"] = (rows[0], 143)
        skills["Prayer"] = (rows[0], 174)
        skills["Magic"] = (rows[0], 205)
        skills["Cooking"] = (rows[2], skills["Ranged"][1])
        skills["Woodcutting"] = (rows[2], skills["Magic"][1])
        skills["Fletching"] = (rows[1], skills["Magic"][1])

        desc = str(uni1 * 5 + uni2 * 5)
        embed = Embed(title="50%", description=desc,
                      colour=0xDEADBF)
        await dembed.edit(embed=embed)

        skills["Fishing"] = (rows[2], skills["Defence"][1])
        skills["Firemaking"] = (rows[2], skills["Prayer"][1])
        skills["Crafting"] = (rows[1], skills["Prayer"][1])
        skills["Smithing"] = (rows[2], skills["Strength"][1])
        skills["Mining"] = (rows[2], skills["Attack"][1])
        skills["Herblore"] = (rows[1], skills["Defence"][1])
        skills["Agility"] = (rows[1], skills["Strength"][1])
        skills["Thieving"] = (rows[1], skills["Ranged"][1])
        skills["Slayer"] = None
        skills["Farming"] = None
        skills["Runecraft"] = (rows[0], 236)
        skills["Hunter"] = None
        skills["Construction"] = (rows[0], 267)

        desc = str(uni1 * 6 + uni2 * 4)
        embed = Embed(title="60%", description=desc,
                      colour=0xDEADBF)
        await dembed.edit(embed=embed)

        # redifing out of order shit
        skills["Slayer"] = (rows[1], skills["Runecraft"][1])
        skills["Hunter"] = (rows[1], skills["Construction"][1])
        skills["Farming"] = (rows[2], skills["Runecraft"][1])

        for index, obj in enumerate(skills):
            # print(obj, parts[index])
            skill_list = list(skills[obj])
            if int(parts[index]) < 10:
                skill_list[0] = skill_list[0] + 5
                skill_list[1] = skill_list[1] - 3
            draw.text(tuple(skill_list),
                      parts[index], (255, 255, 0), font=font)
            if not obj == "Overall":
                draw.text((skill_list[0] + 14, skill_list[1] + 11),
                          parts[index], (255, 255, 0), font=font)
        if not os.path.exists("images"):
            os.makedirs("images")

        desc = str(uni1 * 8 + uni2 * 2)
        embed = Embed(title="80%", description=desc,
                      colour=0xDEADBF)
        await dembed.edit(embed=embed)

        img.save("images/" + name + ".png")

        desc = str(uni1 * 9 + uni2 * 1)
        embed = Embed(title="90%", description=desc,
                      colour=0xDEADBF)
        await dembed.edit(embed=embed)

        await ctx.send("Stats for: " + name, file=File("images/" + name + ".png"))

        os.remove("images/" + name + ".png")

        await dembed.delete(reason="Bot Cleanup")

    @commands.command(disabled=True)
    async def item(self, ctx, name: str):
        """."""
        async with aiohttp.ClientSession() as sess:
            async with sess as clientsess:
                async with clientsess.get('http://services.runescape.com/m=hiscore_' +
                                          'oldschool/index_lite.ws?player=' +
                                          name) as resp:
                    if resp.status != 200:
                        await ctx.message.edit(
                            content=ctx.message.content +
                            "\n`Error: {}`".format(resp.status)
                            .format(name))
                        return
                    json_ = await resp.json()
                    if json_:
                        pass


def setup(bot):
    """."""
    bot.add_cog(Runescape(bot))
