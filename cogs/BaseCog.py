import discord
from discord.ext import commands

import Utils

class BaseCog(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.hybrid_command(name="sample_command", description="this should not be loaded")
    async def _sample_command(self, ctx: commands.Context) -> None:
        await ctx.send("the")

async def setup(bot):
    Utils.pront("Cog BaseCog loading...")
    await bot.add_cog(BaseCog(bot))
    Utils.pront("Cog BaseCog loaded!")