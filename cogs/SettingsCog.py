import discord
from discord.ext import commands

import Utils
from Servers import Servers
from Watcher import Watcher

class SettingsCog(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.hybrid_command(name="channel", description="Sets the channel the bot will keep track of")
    async def _channel(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        if channel is not None:
            Servers.add(ctx.guild.id, Watcher(self.bot, channel))
            await Utils.send(ctx, 'Set!')
            return
        if len(ctx.message.channel_mentions) != 0:
            Servers.add(ctx.guild.id, Watcher(self.bot, ctx.message.channel_mentions[0]))
            await Utils.send(ctx, 'Set!')
            return

        # Didn't provide a valid channel
        await Utils.send(ctx, 'You need to provide a channel!', 'Please mention a channel to watch.')

async def setup(bot):
    Utils.pront("Cog SettingsCog loading...")
    await bot.add_cog(SettingsCog(bot))
    Utils.pront("Cog SettingsCog loaded!")