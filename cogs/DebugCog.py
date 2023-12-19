import discord
import io
import sys
from discord.ext import commands

import Utils
from Servers import Servers

class DebugCog(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.hybrid_command(name="unload", description="unloads the debug cog")
    async def _unload(self, ctx: commands.Context) -> None:
        await self.bot.remove_cog("DebugCog")
        await Utils.send(ctx, 'done')
        await self.bot.tree.sync()
        
    @commands.hybrid_command(name="eval", description="debug cog")
    @commands.is_owner()
    async def _eval(self, ctx: commands.Context, command: str) -> None:
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        command.rstrip("`")
        command.lstrip("`")
        command.lstrip("python")
        try:
            print(eval(command))
        except Exception as e:
            Utils.pront(e, "ERROR")
        sys.stdout = old_stdout
        print(mystdout.getvalue())
        await Utils.send(ctx, title='Command Sent:', description='in:\n```' + command + '```' + '\n\nout:```ansi\n' + str(mystdout.getvalue()) + '```')


    @commands.hybrid_command(name="exec", description="debug cog")
    @commands.is_owner()
    async def _exec(self, ctx: commands.Context, command: str) -> None:
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        command.rstrip("`")
        command.lstrip("`")
        command.lstrip("python")

        try:
            exec(command)
        except Exception as e:
            Utils.pront(e, "ERROR")
        sys.stdout = old_stdout
        print(mystdout.getvalue())
        await Utils.send(ctx, title='Command Sent:', description='in:\n```' + command + '```' + '\n\nout:```ansi\n' + str(mystdout.getvalue()) + '```')


    @commands.hybrid_group(name='list')
    async def list_group(self, ctx: commands.Context):
        pass

    @list_group.command(name='duplicates', description='lists duplicate hashes')
    async def _list_duplicates(self, ctx: commands.Context) -> None:
        
        if not (watcher := Servers.get_watcher(ctx.guild.id)):
            return
        key_val_list = watcher._hashes.items()
        embeds = []
        for hash, jump_urls in key_val_list:
            # No duplicate, continue
            if len(jump_urls) == 1:
                continue

            description = ''
            for url in jump_urls:
                description = f"{description}{url}\n"

            embeds.append(Utils.get_embed(ctx, f"Duplicates for hash {hash.hex()}", description=description))
        if len(embeds) == 0:
            await Utils.send(ctx, "No duplicate hashes detected.")
            return
        if len(embeds) <= 10:
            await ctx.reply(embeds=embeds)
            return
        # Split the list of embeds into sets of 10 to send
        for i in range (0, len(embeds), 10):
            await ctx.reply(embeds=embeds[i:i+10])

async def setup(bot):
    Utils.pront("Cog DebugCog loading...")
    await bot.add_cog(DebugCog(bot))
    Utils.pront("Cog DebugCog loaded!")