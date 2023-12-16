Smash Goblins 2 for the PsVita+
===============================
A discord bot based off of [discord.py](https://github.com/Rapptz/discord.py/) and my [bot core](https://github.com/Sm1mg/discord.py-bot-core/tree/hybrid) that binds to a channel and sends a notification whenever images, audio, videos or urls are reposted.

Installing
----------
**Python 3.11 or higher is required**

Requirements are listed in the ``requirements.txt`` file.

Run the `Bot.py` file to start the bot.

Dotenv Configuration
--------------------

Out of the box, the bot will search for a discord token in the .env named `key`

A maximum per-file memory usage limit is also set via the .env by setting a `max_file_size` variable.
This should be an integer representing the maximum size in bytes.  A value of 0 will disable filesize checking.
**This can be larger than the 500MiB discord limit, as the bot will attempt to download any urls that it encounters that point to a file.**

### Example .env
```env
key="aaaaaaaaaaaaaaaaaaaaaaaaaa.bbbbbb.cccccccccccccccccccccccccccccccccccccc"
# Maximum size of 512MiB
max_file_size=536870912
```
