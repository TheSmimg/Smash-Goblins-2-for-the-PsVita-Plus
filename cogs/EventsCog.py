import asyncio
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

        reference = message.reference.resolved

        if reference is None or isinstance(reference, discord.DeletedReferencedMessage):
            await channel.send(embed=discord.Embed(title="Retrieved message was a NoneType or DeletedReferencedMessage, unable to blacklist."), delete_after=5)
            return

        watcher = Servers.get_watcher(reference.guild.id)
        if not watcher:
            return
        if watcher.channel != message.channel:
            return
        
        await message.delete()
        await watcher.blacklist(message)
        await reference.reply(embed=discord.Embed(title='Blacklisted.'), delete_after=5, mention_author=False)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return 
        watcher = Servers.get_watcher(message.guild.id)
        if not watcher:
            return
        if watcher.channel != message.channel:
            return
        # Task worker that handles calling out users for reposts
        async def repost(match: list[str]):
            try:
                reply = await message.reply(embed=Utils.get_embed(message, "Erm... Repost!!", match[0]))
            except discord.errors.HTTPException as e:
                Utils.pront(e,"ERROR")
                await message.channel.send(embed=Utils.get_embed(title="That was a repost, but you deleted it...", description=f"Next time...\n\n{match[0]}"), delete_after=30)
                return
            await reply.add_reaction('❌')

        async for match in watcher.process(message):
            asyncio.create_task(repost(match))
            

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        if payload.cached_message and payload.cached_message.author.bot:
            return
        watcher = Servers.get_watcher(payload.guild_id)
        if not watcher:
            return
        if payload.channel_id != watcher.channel.id:
            return
        await watcher.raw_delete(payload)

async def setup(bot):
    Utils.pront("Cog EventsCog loading...")
    await bot.add_cog(EventsCog(bot))
    Utils.pront("Cog EventsCog loaded!")