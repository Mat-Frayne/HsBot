"""."""
import asyncio
import aiohttp

hsCards = "https://api.hearthstonejson.com/v1/latest/enUS/cards.json"


@asyncio.coroutine
def get(url=hsCards):
    """Aiohttp GET."""
    with aiohttp.ClientSession() as session:
        resp = yield from session.get(url)
        j = yield from resp.json()
    print(list(set([x["set"] for x in j])))


loop = asyncio.get_event_loop()
loop.run_until_complete(get())


