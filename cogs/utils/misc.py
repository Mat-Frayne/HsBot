#!/usr/bin/env python
"""."""
from difflib import SequenceMatcher
import aiohttp
import discord

DATA = {
    "defaultheader": {"Cache-Control": "no-cache, no-store, must-revalidate",
                      "Pragma": "no-cache"},
    "hsCards": "https://api.hearthstonejson.com/v1/latest/enUS/cards.json",
    "hsBacks": "https://api.hearthstonejson.com/v1/15300/enUS/cardbacks.json",
    "hsCollectable": "https://api.hearthstonejson.com/v1/15300/enUS/cards.collectible.json"
}


def caps(string: str):
    """."""
    return string.title()


def isint(integer: int):
    """."""
    try:
        int(integer)
        return True
    except Exception:
        return False


async def get(url, headers=DATA.get("defaultheader")):
    """Aiohttp GET."""
    try:
        with aiohttp.ClientSession() as session:
            resp = await session.get(url, header=headers)
            j = await resp.json()
        return j
    except Exception as exc:
        print(exc)
        return {"error": exc}


async def diffrence(stime, ftime):
    """."""
    min_, sec_ = divmod(ftime - stime, 60)
    hour_, min_ = divmod(min_, 60)
    day_, hour_ = divmod(hour_, 24)
    uptime = ""
    if day_ > 0:
        uptime += str(round(day_)) +\
            " " + (day_ == 1 and "day" or "days") + ", "
    if uptime or hour_ > 0:
        uptime += str(round(hour_)) +\
            " " + (hour_ == 1 and "hour" or "hours") + ", "
    if uptime or min_ > 0:
        uptime += str(round(min_)) +\
            " " + (min_ == 1 and "minute" or "minutes") + \
            ", "
    uptime += str(round(sec_)) +\
        " " + (sec_ == 1 and "second" or "seconds")
    return uptime


async def user(ctx, username):
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


def similar(valuea, valueb):
    """Return the similarity ratio between 2 items."""
    return SequenceMatcher(None, valuea, valueb).ratio()
