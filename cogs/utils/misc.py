"""."""
from difflib import SequenceMatcher
import asyncio
import aiohttp
import discord

defaultheader = {"Cache-Control": "no-cache, no-store, must-revalidate",
                 "Pragma": "no-cache"}
hsCards = "https://api.hearthstonejson.com/v1/latest/enUS/cards.json"
hsBacks = "https://api.hearthstonejson.com/v1/15300/enUS/cardbacks.json"
hsCollectable = "https://api.hearthstonejson.com/v1/15300/enUS/cards.collectible.json"



def caps(str):
    """."""
    return str.title()


def isint(x):
    """."""
    try:
        int(x)
        return True
    except:
        return False


@asyncio.coroutine
def get(url, headers=defaultheader):
    """Aiohttp GET."""
    try:
        with aiohttp.ClientSession() as session:
            resp = yield from session.get(url)
            j = yield from resp.json()
        return j
    except Exception as e:
        print(e)
        return {"error": e}


@asyncio.coroutine
def diffrence(stime, ftime):
    """."""
    m, s = divmod(ftime - stime, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    uptime = ""
    if d > 0:
        uptime += str(round(d)) +\
            " " + (d == 1 and "day" or "days") + ", "
    if len(uptime) > 0 or h > 0:
        uptime += str(round(h)) +\
            " " + (h == 1 and "hour" or "hours") + ", "
    if len(uptime) > 0 or m > 0:
        uptime += str(round(m)) +\
            " " + (m == 1 and "minute" or "minutes") + \
            ", "
    uptime += str(round(s)) +\
        " " + (s == 1 and "second" or "seconds")
    return uptime


@asyncio.coroutine
def user(ctx, username):
    """."""
    return discord.utils.get(ctx.message.channel.server.members,
                             name=username.strip()) or \
        discord.utils.get(ctx.bot.get_all_members(),
                          name=username.strip()) or \
        discord.utils.find(
            lambda m: m.name.lower() == username.strip().lower(),
            ctx.message.channel.server.members) or \
        discord.utils.find(
            lambda m: m.name.lower() == username.strip().lower(),
            ctx.bot.get_all_members()) or None


def similar(a, b):
    """Return the similarity ratio between 2 items."""
    return SequenceMatcher(None, a, b).ratio()