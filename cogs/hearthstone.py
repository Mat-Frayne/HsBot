"""."""
from difflib import SequenceMatcher
from discord.ext import commands
import asyncio
from .utils import (misc, data)
import discord
import time


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
        argl = arg.lower()
        cards = yield from self.get_cards(argl)
        if len(cards) < 1:
            yield from self.bot.say("No close matches found.")
            return
        embed = discord.Embed(description='')
        embed.title = cards[0]["name"]
        embed.url = data["urls"]["hs_image_base_url"].format(cards[0]["id"])
        embed.set_image(
            url=data["urls"]["hs_image_base_url"].format(cards[0]["id"]))
        if len(cards) > 1:
            embed.set_footer(
                text="{} more cards found, type {}more to see the next {}"
                .format(len(cards) - 1, ctx.prefix,
                        len(cards) - 1 if len(cards) - 1 < 6 else 6))
        if cards[0].get("dust", None):
            embed.add_field(
                name="Dust",
                value="Crafting (norm | gold): {:>10} | {:<}\n"
                .format(cards[0]["dust"][0] if len(
                        cards[0]["dust"]) > 0 else "N/A",
                        cards[0]["dust"][1] if len(
                            cards[0]["dust"]) > 1 else "N/A") +
                "Disenchant (norm | gold): {:>5} | {:<5}"
                .format(cards[0]["dust"][2] if len(
                        cards[0]["dust"]) > 2 else "N/A",
                        cards[0]["dust"][3] if len(
                        cards[0]["dust"]) > 3 else "N/A",))
        yield from self.bot.say(embed=embed)
        try:
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
            raise
        yield from self._search_response(ctx, cards)

    @asyncio.coroutine
    def get_cards(self, query):
        """."""
        top = []

        for card in [tyu for tyu in self.bot.hs["cards"] if
                     tyu.get("type", "Other") not in ["HERO", "HERO_POWER"]]:
            if card.get("set", None) not in ['NONE', None]:
                sim = SequenceMatcher(None, card["name"].lower(), query).ratio()
                if sim > .8 or\
                        query in card["name"].lower():
                    top.append(card)

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
    def _search_response(self, ctx, arr):
        """."""
        def check(msg):
            """."""
            return msg.content == ctx.prefix + "more"
        msg = yield from self.bot.wait_for_message(
            check=check, timeout=120)
        if msg:
            yield from self.bot.say("!more sent")

    @asyncio.coroutine
    def _classes_response(self, ctx, outmess):
        """."""
        def check(mess):
            """."""
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
