import discord
from discord.ext import commands

import Utils
from Servers import Servers

class EventsCog(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if not payload.member or payload.member == self.bot.user:
            return
        if payload.emoji.name != "❌":
            return
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        for reaction in message.reactions:
            if reaction.emoji == payload.emoji.name:
                break
                
        if not reaction.me:
            return

        await message.delete()

        reference = message.reference.resolved

        if reference is None or isinstance(reference, discord.DeletedReferencedMessage):
            await channel.send(embed=discord.Embed(title="Retrieved message was a NoneType or DeletedReferencedMessage, unable to blacklist."), delete_after=5)
            return

        watcher = Servers.get_watcher(reference.guild.id)
        await watcher.blacklist(reference)

        await reference.reply(embed=discord.Embed(title='Blacklisted.'), delete_after=5, mention_author=False)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return 
        watcher = Servers.get_watcher(message.guild.id)
        if watcher is not None:
            await watcher.process(message)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        watcher = Servers.get_watcher(payload.guild_id)
        if watcher is not None:
            await watcher.raw_delete(payload)

async def setup(bot):
    Utils.pront("Cog EventsCog loading...")
    await bot.add_cog(EventsCog(bot))
    Utils.pront("Cog EventsCog loaded!")