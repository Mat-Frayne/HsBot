"""."""
from asyncio import TimeoutError as Te_
from datetime import datetime

from discord.ext import commands
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select


class Commands:
    """."""

    def __init__(self, bot):
        """."""
        self.bot = bot

    @commands.group(invoke_without_command=False)
    async def command(self, ctx):
        """."""
        pass

    @command.command()
    async def add(self, ctx, cmd: str = "", *, output: str = ""):
        """."""
        if len(cmd) < 3:
            await ctx.send(
                "Command must be longer then 3 characters. " +
                "\n\t(!command add `<command>` `<output>`)")
            return
        if len(output.strip()) < 1:
            await ctx.send(
                "Output must be longer then 1 characters not including spaces." +
                " \n\t(!command add `<command>` `<output>`)")
            return
        if not (cmd[0].isalpha() or cmd[0].isdigit()):
            await ctx.send("Error: command must start with [a-z, 0-9] not '{}'".format(cmd[0]))
            return
        if len(cmd) > 40:
            await ctx.send("Error: command to long {}/40.".format(len(cmd)))
            return
        if len(output) < 1:
            await ctx.send("Error: No output given.")
            return
        if len(output) > 500:
            await ctx.send("Error: Output to long {}/500.".format(len(output)))
            return

        comms = self.bot.models.commands
        statement = select([comms]).where(comms.c.Command == cmd.strip())
        query = self.bot.conn.execute(statement).first()
        if query:
            await ctx.send("Already a command {}.".format(cmd.strip()))
            return
        mess = await ctx.send(
            "**Is this correct?**```RUBY\nCommand:\n\t{}\n\nOutput:\n\t{}```".format(cmd, output))
        await mess.add_reaction('\u2705')
        await mess.add_reaction('\u274C')

        def check(react, user):
            """."""
            return user.id == ctx.message.author.id and \
                react.emoji.encode(
                    'unicode-escape') in [b"\\u2705", b"\\u274c"]
        try:
            msg = await self.bot.wait_for('reaction_add', check=check, timeout=60)
        except Te_:
            await mess.delete()
            await ctx.send("Command {} timed out.".format(cmd))
            return
        if msg[0].emoji.encode('unicode-escape') == b"\\u2705":
            await mess.delete()

            try:
                query = self.bot.models.commands.insert().values(
                    Command=cmd.strip(),
                    Created_at=datetime.utcnow(),
                    Created_by=ctx.author.id,
                    Result=output.strip(),
                    Global=1,
                    Channel=ctx.channel.id
                )
                self.bot.conn.execute(query)
            except Exception as exc:
                await ctx.send("Error adding {} command to database.".format(cmd.strip()))
                user = await self.bot.application_info()
                user = self.bot.get_user(user.owner.id)
                await user.send(exc)
                return

            await ctx.send("Command {} Sucessfully added.".format(cmd))
        elif msg[0].emoji.encode('unicode-escape') == b"\\u2705":
            await mess.delete()
            await ctx.send("Command {} Cancelled.".format(cmd))

    @command.command(aliases=["remove"])
    async def delete(self, ctx, cmd):
        """."""
        comms = self.bot.models.commands
        statement = select([comms]).where(comms.c.Command == cmd.strip())
        query = self.bot.conn.execute(statement).first()
        if not query:
            await ctx.send("No custom command {} found.".format(cmd.strip()))
            return
        owner = await self.bot.application_info()
        if not query[2] in [ctx.message.author.id, owner.owner.id]:
            await ctx.send("You do not have permission to delete this command.")
            return
        try:
            statement = comms.delete().where(comms.c.Command == cmd.strip())
            query = self.bot.conn.execute(statement)
            await ctx.send("Command {} sucessfully removed.".format(cmd.strip()))
        except Exception:
            await ctx.send("error removing command")

    @command.command()
    async def info(self, ctx, cmd:str):
        """."""
        await ctx.send("working")

    async def on_message(self, message):
        """."""
        cmd = message.content.split(" ")[0]
        if cmd[0] == await self.bot.get_prefix(message):
            comms = self.bot.models.commands
            statement = select([comms]).where(comms.c.Command == cmd[1:])
            query = self.bot.conn.execute(statement).first()
            if query:
                await message.channel.send(query[3])


def setup(bot):
    """."""
    bot.add_cog(Commands(bot))

# !eval
# from subprocess import PIPE, Popen
# pipe = Popen("tracert sydney77.discord.gg", shell=True, stdout=PIPE).stdout
# output = pipe.read()
# print(output)
