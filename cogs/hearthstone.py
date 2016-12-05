"""."""
from difflib import SequenceMatcher
from discord.ext import commands
from .utils import (misc, data)
import asyncio
import discord
import time
import re


class Hearthstone:
    """."""

    def __init__(self, bot):
        """."""
        self.bot = bot
        self.mutators = {y: x for x, y in enumerate(data["mutators_array"])}

    @commands.command(name="hs", pass_context=True,
                      aliases=["hearthstone", "Hs", "HS"])
    @asyncio.coroutine
    def _hs(self, ctx, *, arg: str):
        """Search Hearthstone."""
        pullargs = re.findall(r'-(.*?)(\s|-|$)', arg)
        args = {}
        for x in pullargs:
            try:
                arg1 = re.findall(r'(.*?)=', x[0])
                arg2 = re.findall(r'=(.*?)$', x[0])
                arg = arg.replace("-" + x[0], "")
                args[arg1[0].lower()] = arg2[0]
            except:
                pass
        argl = arg.lower().strip()
        ratio = 0.8
        if args.get("ratio"):
            try:
                ratio = int(args.get("ratio", "0.8"))
                if ratio < 0 > 1:
                    ratio = 0.8
            except:
                pass
        if args.get("id", None):
            cards = [x for x in self.bot.hs["cards"] if
                     x["id"] == args.get("id")]
        else:
            cards = yield from self.get_cards(argl, ratio, args)
        if len(cards) < 1:
            yield from self.bot.say("No close matches found.")
            return
        embed = discord.Embed(description='')
        embed.title = cards[0]["name"]
        embed.url = data["urls"]["hs_image_base_url"].format(cards[0]["id"])
        embed.set_image(
            url=data["urls"]["hs_image_base_url"].format(cards[0]["id"]))
        text = "{} more card{} found, type {}more to see {}."
        if len(cards) > 1:
            c = len(cards) - 1
            k = "it" if c is 1 else "them"
            embed.set_footer(
                text=text
                .format(
                    len(cards) - 1, "s" if c is not 1 else "", ctx.prefix,
                    k if (len(cards) - 1) < 6 else "the next 6"))
        info = ""
        if cards[0].get("type", None):
            info = info + "Type: {}".format(cards[0].get("type", "").title())
        if cards[0].get("cost", None):
            info = info + "\nMana Cost: {}\t".format(cards[0].get("cost"))
        if cards[0].get("playerClass", None):
            info = info + "\nClass: {}\t".format(
                cards[0].get("playerClass", "").title())
        if cards[0].get("attack", None):
            info = info + "Attack: {}\t".format(cards[0].get("attack"))
        if cards[0].get("health", None):
            info = info + "Health: {}\t".format(cards[0].get("health"))
        if cards[0].get("durability", None):
            info = info + "Durability: {}\t".format(cards[0].get("durability"))
        embed.add_field(
            name="Info:",
            value=info + "\n" +
            re.sub(
                r"<.{1,2}>|\[x\]", "",
                cards[0].get("text", ""))
            .strip().replace("\n", " ") + "\n" +
            cards[0].get("howToEarn", ""))
        if cards[0].get("dust", None):
            table = "{:<8}     {:>12}     {:>14}".format(
                "Type", "Crafting", "Disenchant")
            cnorm = cards[0]["dust"][0] if len(
                cards[0]["dust"]) > 0 else "N/A"
            cgold = cards[0]["dust"][1] if len(
                cards[0]["dust"]) > 1 else "N/A"
            dnorm = cards[0]["dust"][2] if len(
                cards[0]["dust"]) > 2 else "N/A"
            dgold = cards[0]["dust"][3] if len(
                cards[0]["dust"]) > 3 else "N/A"
            table = table + "\n{:<6}     {:>12}     {:>20}".format(
                "Normal", cnorm, dnorm)
            table = table + "\n{:<9}     {:>12}     {:>20}".format(
                "Gold", cgold, dgold)
            embed.add_field(name="Dust:", value=table, inline=False)
        yield from self.bot.say(embed=embed)
        try:
            if ctx.message.channel.id != "159566466243493888":
                k = self.bot.database.table_data(
                    "Searches", "Card", cards[0]["id"])
                if len(k) < 1:
                    self.bot.database.insert_row(
                        "Searches",
                        {"Last_used": time.time(), "Card": cards[0]["id"],
                         "Count": "1"})
                else:
                    self.bot.database.change_data(
                        "Searches",
                        {"Count": str(int(k[0]["Count"]) + 1)},
                        {"Card": cards[0]["id"]})
        except:
            pass
        if len(cards) > 1:
            msg = yield from self.bot.wait_for_message(
                author=ctx.message.author)
            if msg.content == ctx.prefix + "more":
                if len(cards) == 2:
                    arg = "-id={}".format(
                        cards[1].get("id", None))
                    yield from ctx.invoke(self._hs, arg=arg)
                    return
                embed = discord.Embed()
                for index, x in enumerate(cards[1:7]):
                    out = ""
                    if x.get("type"):
                        out = out + "Type: " + x.get("type", "").title()
                    if x.get("cost"):
                        out = out + "\nCost: " + str(x.get("cost"))
                    if x.get("attack"):
                        out = out + "\nAttack: " + str(x.get("attack"))
                    if x.get("health"):
                        out = out + "\nHealth: " + str(x.get("health"))
                    embed.add_field(
                        name="{}: {}".format(index, x.get("name", "N/A")),
                        value=out)
                embed.set_footer(
                    text=(
                        "Type a number from 0-{} for more infomation"
                        .format((len(cards) - 1) if len(cards) < 5 else "5") +
                        " on a card."))
                yield from self.bot.say(embed=embed)
                msg = yield from self.bot.wait_for_message(
                    author=ctx.message.author)
                if misc.isint(msg.content.strip(ctx.prefix)) and\
                        (0 <= int(msg.content.strip(ctx.prefix)) <
                            len(cards) - 1):
                    arg = "-id={}".format(
                        cards[int(msg.content) + 1].get("id", None))
                    yield from ctx.invoke(self._hs, arg=arg)

    @asyncio.coroutine
    def get_cards(self, query, ratio, args):
        """."""
        top = []
        print(args)
        for card in [tyu for tyu in self.bot.hs["cards"]]:
            if card.get("set", None) not in ['NONE', None]:
                sim = SequenceMatcher(
                    None, card["name"].lower(), query).ratio()
                if sim > ratio or\
                        query in card["name"].lower():
                    top.append(card)
        if args.get("health", None):
            top = [x for x in top if str(x.get("health")) ==
                   str(args.get("health", None))]
        if args.get("attack", None):
            top = [x for x in top if x.get("attack", None) ==
                   args.get("attack", None)]
        if args.get("durability", None):
            top = [x for x in top if x.get("durability", None) ==
                   args.get("durability", None)]
        if args.get("mana", None):
            top = [x for x in top if x.get("cost", None) ==
                   args.get("mana")]
        if args.get("cost", None):
            top = [x for x in top if x.get("cost", None) ==
                   args.get("cost")]
        if args.get("class", None):
            top = [x for x in top if x.get("playerClass", None).lower() ==
                   args.get("class").lower()]
        if args.get("mechanic", None):
            top = [x for x in top if args.get("mechanic").upper() in
                   x.get("mechanics", [])]

        def sortkey_mutators(k):
            """."""
            return self.mutators.get(k.get("set", "NONE"), 9999)

        return sorted(top, key=sortkey_mutators)

    @commands.command(name="classes", pass_context=True,
                      aliases=["class's", "Class's", "Classes"])
    @asyncio.coroutine
    def _classes(self, ctx):
        """List all classes."""
        embed = discord.Embed(description='')
        embed.title = 'Hearthstone Classes'
        embed.url = 'http://google.com'
        embed.set_footer(
            text="Type a number from 0 - {} for more info on a class! "
            .format(len(data["player_classes"]) - 1) + "(has 2 min timer)")
        for index, x in enumerate(data["player_classes"]):
            class_ = misc.caps(x)
            cards = len(
                [i for i in self.bot.hs.get("cards", []) if
                 i.get("playerClass", None) == x])
            power = data["player_classes"][x]["power"]
            field = "Unique cards: {}\nHero Power: {}".format(cards, power)
            embed.add_field(name="{}: {}\n".format(index, class_), value=field)
        outmess = yield from self.bot.say(embed=embed)
        yield from self._classes_response(ctx, outmess)

    @commands.command(name="class", pass_context=True,
                      aliases=["Class"])
    @asyncio.coroutine
    def _class(self, ctx, *, arg: str):
        """Get class info."""
        if arg.upper().strip() not in data["player_classes"]:
            yield from self.bot.say("cant find class {}\ use {}".format(arg))
            return
        hero = "DRUID"
        embed = discord.Embed(description='test')
        embed.title = hero.title()
        embed.url = "http://" + self.bot.url + "/TBA"
        u = "http://139.59.234.223/static/images/images/DRUID/main.png"
        #  .format(self.bot.url, hero)
        # u = "https://i.ytimg.com/vi/yaqe1qesQ8c/maxresdefault.jpg"
        print(u)
        embed.set_image(url=u)
        yield from self.bot.say(embed=embed)
        yield from self.bot.say(embed.image)

    @commands.command(name="card", pass_context=True,
                      aliases=["Card"])
    @asyncio.coroutine
    def _card(self, ctx, *, arg: str):
        """Search for a card."""
        pass

    @commands.command(name="backs", pass_context=True,
                      aliases=["Backs"])
    @asyncio.coroutine
    def _backs(self, ctx):
        """List card backs."""
        pass

    @commands.command(name="back", pass_context=True,
                      aliases=["Back"])
    @asyncio.coroutine
    def _back(self, ctx, *, arg: str):
        """Search for a card back."""
        pass

    # @commands.command(name="factions", pass_context=True,
    #                   aliases=["Factions"])
    # @asyncio.coroutine
    # def _factions(self, ctx, *, arg: str):
    #     """List all factions."""
    #     pass
    @commands.command(name="powers", pass_context=True,
                      aliases=["Powers"])
    @asyncio.coroutine
    def _powers(self, ctx):
        """List all hero powers."""
        pass

    # @commands.command(name="spells", pass_context=True,
    #                   aliases=["Spells"])
    # @asyncio.coroutine
    # def _podwers(self, ctx, *, arg: str):
    #     """List all her spells."""
    #      spells = [x for x in self.bot.hs["cards"] if x["type"] == "SPELL"]
    #     print(spells)
    #     embed = discord.Embed(description='')
    #     embed.title = 'Hearthstone Classes'
    #     embed.url = 'http://google.com'
    #     embed.set_footer(
    #         text="type !spell <spell_name> for more info on that spell")
    #     for x in range(0, len(spells), 10):
    #         print(x)
    #   embed.add_field(name=" _", value="\n".join([i["name"] for i in x]))

    #     yield from self.bot.say(embed=embed)

    @commands.command(name="quests")
    @asyncio.coroutine
    def _quests(self):
        """."""
        pass

    @commands.command
    @asyncio.coroutine
    def test(self, ctx, *, arg: str=None):
        """."""
        pass

    # Responses

    @asyncio.coroutine
    def _classes_response(self, ctx, outmess):
        """."""
        def check(mess):
            """."""
            mess.content = mess.content.strip(ctx.prefix)
            return misc.isint(mess.content) and\
                (0 <= int(mess.content) < len(data["player_classes"]))

        msg = yield from self.bot.wait_for_message(
            author=ctx.message.author, check=check, timeout=120)
        if msg:
            yield from self.bot.delete_message(msg)
            yield from self.bot.say(
                [x for x in data["player_classes"]][int(msg.content)])


def setup(bot):
    """."""
    bot.add_cog(Hearthstone(bot))
