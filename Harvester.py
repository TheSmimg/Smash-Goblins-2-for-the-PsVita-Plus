import aiohttp
import asyncio
import discord
import hashlib
import validators
# Harvests hashed data sources from a message
async def harvest_message(message: discord.Message) -> set[str]:
    urls = Harvester.parse_urls(message.content)
    hashes = set()

    # Share aiohttp.ClientSession over all file_hash_from_url tasks
    async with aiohttp.ClientSession() as session:
        async with asyncio.TaskGroup() as group:
            for attachment in message.attachments:
                group.create_task(Harvester.get_attachment_hash(attachment, hashes))
            for url in urls:
                group.create_task(Harvester.file_hash_from_url(url, session, hashes))

    if len(hashes) < len(message.attachments) + len(urls):
        # If a file couldn't be hashed by url, just hash the url
        for url in urls:
            hashes.add(hashlib.md5(url.encode()).hexdigest())
    return hashes
    

class Harvester:
    def parse_urls(message: str) -> set[str]:
        urls = set()
        for word in message.split():
            if validators.url(word):
                urls.add(word)
        return urls


    async def get_attachment_hash(attachment: discord.Attachment, hashes: set[str]) -> str:
        hashes.add(hashlib.md5(await attachment.read()).hexdigest())

    
    async def file_hash_from_url(url: str, session: aiohttp.ClientSession, hashes: set[str]) -> str:
        async with session.get(url) as response:
            if not response.ok:
                return
            # Check for disallowed header content types
            if response.content_type.split("/")[0] in ["application", "font", "example", "message", "model", "multipart", "text"]:
                return
            hashes.add(hashlib.md5(await response.read()).hexdigest())
    
    