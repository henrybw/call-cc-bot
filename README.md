# call/cc bot
Discord bot that passes continuations to requested channels.

# Usage

    ~(call/cc #channel [context])

~call~ continue the current ~continuation~ conversation in another channel on
this server, where `context` is the number of previous messages to repost
(0, by default).

The bot expects `#channel` to be a channel reference (i.e. appearing as a
clickable link). Discord should automatically convert this for you.

# Setup

Tools:

* [Git](https://git-scm.com/) (which you needed to clone this repository)
* [Python 3](https://www.python.org/)

Libraries:

* [discord.py](https://github.com/Rapptz/discord.py)

Installation:

    python3 -m pip install -U discord.py

Operation:

    python3 call-cc-bot.py

## Secrets

If you try to run call/cc bot immediately, you'll notice that it will fail
because it cannot find the `secrets` module. For access security, all operations
exposed by the Discord API require a token for authenticating the bot as a user.
In order to use this access token with call-cc-bot, create a new file in the
repository called `secrets.py`, and define the following constants:

    BOT_TOKEN="your-bot-auth-token"

This file is explicitly excluded from the repository (via .gitignore), to
prevent sensitive tokens from being pushed publicly.
