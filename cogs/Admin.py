#!/usr/bin/env python
"""."""
import asyncio
import inspect
import io
import subprocess
import textwrap
import traceback
from contextlib import redirect_stdout

import discord
from discord.ext import commands
from sys import platform

class Admin:
    """."""

    def __init__(self, bot):
        """."""
        self.bot = bot
        self.extensions = ["Hearthstone", "Runescape", "Commands"]
        self._last_result = None
        self.sessions = set()
        for extension in self.extensions:
            try:
                self.bot.load_extension('cogs.' + extension)
            except Exception as exc:
                print('Failed to load extension {}\n{}: {}'
                      .format(extension, type(exc).__name__, exc))

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @staticmethod
    def get_syntax_error(err):
        if err.text is None:
            return f'```py\n{err.__class__.__name__}: {err}\n```'
        return f'```py\n{err.text}{"^":>{err.offset}}\n{err.__class__.__name__}: {err}```'

    @commands.command(name='reload', aliases=["r"], hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module: str = "all"):
        """Reload a module."""
        out = ""
        if "all" in module.lower():
            for extension in self.extensions + ["Admin"]:
                try:
                    self.bot.unload_extension('cogs.' + extension)
                    self.bot.load_extension('cogs.' + extension)
                    out = "{}\nReloaded {}".format(out, 'cogs.' + extension)
                except Exception as exc:
                    out = "{}\nFailed to reload {}\n\t{}: {}"\
                        .format(out, extension, type(exc).__name__, exc)
        else:
            try:

                self.bot.unload_extension(module)
                self.bot.load_extension(module)
                out = "Reloaded {}".format(module)
            except Exception as exc:
                out = '{}: {}'.format(type(exc).__name__, exc)
        await ctx.send(out)

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'db': self.bot.models,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as exc:
            return await ctx.send(f'```py\n{exc.__class__.__name__}: {exc}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except Exception:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')
    
    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def repl(self, ctx):
        """Launches an interactive REPL session."""
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            '_': None,
        }

        if ctx.channel.id in self.sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.')
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')

        def check(chk):
            """."""
            return chk.author.id == ctx.author.id and \
                chk.channel.id == ctx.channel.id and \
                chk.content.startswith('`')

        while True:
            try:
                response = await self.bot.wait_for('message', check=check, timeout=10.0 * 60.0)
            except asyncio.TimeoutError:
                await ctx.send('Exiting REPL session.')
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self.sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as err:
                    await ctx.send(self.get_syntax_error(err))
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception:
                value = stdout.getvalue()
                fmt = f'```py\n{value}{traceback.format_exc()}\n```'
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f'```py\n{value}{result}\n```'
                    variables['_'] = result
                elif value:
                    fmt = f'```py\n{value}\n```'

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await ctx.send('Content too big to be printed.')
                    else:
                        await ctx.send(fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as err:
                await ctx.send(f'Unexpected error: `{err}`')

    @commands.is_owner()
    @commands.command()
    async def ping(self, ctx):
        """Ping to sydney77's ip."""
        await ctx.message.add_reaction('\u2705')
        if platform == "linux":
            mycmd = subprocess.getoutput("ping -c 10 168.1.24.83")
        else:
            mycmd=subprocess.getoutput("ping 168.1.24.83")
        resp = mycmd.decode("utf-8")
        await ctx.send("```prolog\n{}```".format(resp))

    @commands.is_owner()
    @commands.command()
    async def trace(self, ctx, server):
        """."""
        await ctx.message.add_reaction('\u2705')
        if not server.endswith(".discord.gg"):
            server = server + ".discord.gg"
        p = subprocess.Popen(
            ["tracert.exe", server], stdout=subprocess.PIPE)
        resp = p.communicate()[0].decode("utf-8")
        await ctx.send("```prolog\n" + resp + "```")

    # git clone -b rewrite https://github.com/Mat-Frayne/HsBot.git
def setup(bot):
    """."""
    bot.add_cog(Admin(bot))
