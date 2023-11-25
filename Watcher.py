import asyncio
import discord

import Harvester
import Utils

class Watcher:
    def __init__(self, bot: discord.Client, channel: discord.abc.GuildChannel):
        """
        A class that contains all of the hash information about a channel.
        
        Attributes
        ----------
        is_up_to_date : `asyncio.Event()`
            An event that is set when the Watcher is not processing messages in this channel.
        
        Methods
        -------
        async process(message: `discord.Message`):
            Processes the supplied message and checks if it's media is a repost.
        async blacklist(message: `discord.Message`):
            Adds the supplied message to the internal blacklist.
        async raw_delete(payload: discord.RawMessageDeleteEvent):
            Processes a RawMessageDeleteEvent to avoid detecting deleted messages as reposts.
        
            
        """
        self.channel = channel
        self._hashes = {}
        self._blacklist = {}
        self.is_up_to_date = asyncio.Event()
        
        # Concurrent method that iterates over all messages in a channel
        # populating the _hashes dict with media hashes
        async def worker(self):
            # Set bot to appear idle as a hint that the bot is busy
            await bot.change_presence(status=discord.Status.idle)
            async for msg in channel.history(limit=None, oldest_first=True):
                for source in await Harvester.harvest_message(msg):
                    # If this hash is already here, append instead of replacing
                    if self._hashes.get(source) is not None:
                        self._hashes[source].append(msg.jump_url)
                        continue
                    self._hashes[source] = [msg.jump_url]
            # Set bot to appear online
            await bot.change_presence()

        def finish_worker(worker):
            self.is_up_to_date.set()
            del worker

        self.task = asyncio.create_task(worker(self))
        self.task.add_done_callback(finish_worker)


    async def process(self, message: discord.Message) -> bool:
        """
        Processes the supplied message and checks if it's media is a repost.

        Parameters
        ----------
        message : `discord.Message`
            The message to process.
        
        Returns
        -------
        `True`:
            Returns True when the message's media has been reposted.
        `False`:
            Returns False when the message's media has not been posted before.
        """
        await self.is_up_to_date.wait()
        self.is_up_to_date.clear()
        for source in await Harvester.harvest_message(message):
            if self._blacklist.get(source) is not None:
                break
            # No match
            if ( match := self._hashes.get(source) ) is None:
                self._hashes[source] = [message.jump_url]
                continue
            # Match & permitted
            self._hashes[source].append(message.jump_url)
            self.is_up_to_date.set()
            reply = await message.reply(embed=Utils.get_embed(message, "Erm... Repost!!", content=match[0]))
            await reply.add_reaction('❌')
            return True
        self.is_up_to_date.set()
        return False
    

    async def blacklist(self, message: discord.Message) -> None:
        """
        Adds the supplied message to the internal blacklist.
        This prohibits process() from detecting it as a repost.
        The supplied message *must* already be in the internal hash list.

        Parameters
        ----------
        message : `discord.Message`
            The message to add to the blacklist.
        """
        await self.is_up_to_date.wait()
        self.is_up_to_date.clear()
        for source in await Harvester.harvest_message(message):
            self._blacklist[source] = message.jump_url
            self._hashes.pop(source)
        self.is_up_to_date.set()

    
    async def raw_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        """
        Processes a RawMessageDeleteEvent to avoid detecting deleted messages as reposts.

        This will first check if the message is still within the bots message cache.
        If it is not, it will delete any hashes belonging to a message of the same ID.

        Parameters
        ----------
        payload : `discord.RawMessageDeleteEvent`
            The RawMessageDeleteEvent to process.  These are provided by the `on_raw_message_delete` event in discord.
        """
        if payload.cached_message:
            for source in await Harvester.harvest_message(payload.cached_message):
                if self._blacklist.get(source):
                    self._blacklist.pop(source)
                    continue
                if self._hashes.get(source):
                    self._hashes[source].remove(payload.cached_message.jump_url)
                    # If removing this url empties the list, remove the entry
                    if len(self._hashes[source]) == 0:
                        self._hashes.pop(source)
            return
        # Check _hashes
        for key, value in self._hashes.items():
            for url in value:
                if int(url.split("/")[-1]) == payload.message_id:
                    self._hashes[key].remove(url)
                    # If removing this url empties the list, remove the entry
                    if len(self._hashes[key]) == 0:
                        self._hashes.pop(key)
                    break
        # Check _blacklist
        for key, value in self._blacklist.items():
            if int(value.split("/")[-1]) == payload.message_id:
                self._blacklist.pop(key)
                break