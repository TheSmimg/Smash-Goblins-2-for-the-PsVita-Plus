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
        if not channel and not ctx.message.channel_mentions:
            # Didn't provide a valid channel
            await Utils.send(ctx, 'You need to provide a channel!', 'Please mention a channel to watch.')
        Servers.add(ctx.guild.id, Watcher(self.bot, 
                                          channel if channel else ctx.message.channel_mentions[0]))
        await Utils.send(ctx, 'Set!')
        return

async def setup(bot):
    Utils.pront("Cog SettingsCog loading...")
    await bot.add_cog(SettingsCog(bot))
    Utils.pront("Cog SettingsCog loaded!")