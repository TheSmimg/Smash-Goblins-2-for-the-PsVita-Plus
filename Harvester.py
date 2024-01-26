import aiohttp
import asyncio
import discord
import hashlib
import os
import validators

import Utils

# Harvests hashed data sources from a message
async def harvest_message(message: discord.Message) -> set[str]:
    urls = Harvester.parse_urls(message.content)
    hashes = set()

    # Share aiohttp.ClientSession over all file_hash_from_url tasks
    async with aiohttp.ClientSession() as session:
        async with asyncio.TaskGroup() as group:
            for attachment in message.attachments:
                group.create_task(Harvester.hash_file(attachment.url, session, hashes))
            for url in urls:
                group.create_task(Harvester.hash_file(url, session, hashes))

    if len(hashes) < len(message.attachments) + len(urls):
        # If a file couldn't be hashed by url, just hash the url
        for url in urls:
            if Harvester.max_size != 0 and len(url) > Harvester.max_size:
                Utils.pront("...Url length exceeded maximum memory usage limit, seriously??", "WARNING")
                continue
            hashes.add(await Harvester.md5_hash_handler(url.encode()))
    return hashes
    

class Harvester:
    
    # Parse max size from dotenv
    if max_size := os.environ.get('max_file_size'):
        try:
            max_size = int(max_size)
        except ValueError as e:
            raise ValueError("Maximum filesize in .env must be integer-convertible")
    else:
        max_size = 0
    

    def parse_urls(message: str) -> set[str]:
        urls = set()
        for word in message.split():
            if validators.url(word):
                urls.add(word)
        return urls


    async def hash_file(url: str, session: aiohttp.ClientSession, hashes: set[str]) -> None:
        async with session.get(url) as response:
            if not response.ok:
                return
            # Check for disallowed header content types
            if response.content_type.split("/")[0] in ["application", "font", "example", "message", "model", "multipart", "text"]:
                return
            content = bytes()
            while chunk := await response.content.readany():
                content+=chunk
                if len(content) > Harvester.max_size:
                    Utils.pront("URL response size exceeded maximum memory usage limit, aborting.", "WARNING")
                    return
                
            hashes.add(await Harvester.md5_hash_handler(content))

    def __md5sum(data: bytes) -> bytes:
        return hashlib.md5(data).digest()

    async def md5_hash_handler(data: bytes) -> bytes:
        # hashlib releases the GIL for large hashes, take advantage of that here
        return await asyncio.to_thread(Harvester.__md5sum, data)