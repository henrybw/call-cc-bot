import discord
from collections import deque
from sys import maxsize
import secrets

client = discord.Client()

USAGE_TEXT = ("usage: `~(call/cc #channel [context])`\n\n"
              "~~call~~ continue the current ~~continuation~~ conversation in another "
              "channel on this server, where `context` is the number of previous "
              "messages to repost (0, by default).")

def handle(author):
    return author.nick if author.nick else author.name

@client.event
async def on_ready():
    print("call/cc bot ready")

@client.event
async def on_message(msg):
    server = msg.server
    if not server:
        return
    if not msg.content.startswith("~("):
        return

    cmd = msg.content.split(' ')

    # this bot is uselessly pedantic about being fed s-expressions *only*.
    if not cmd[-1].endswith(")"):
        await client.send_message(msg.channel,
                                  "expected a `)` to close `(`\n\n%s" % (USAGE_TEXT,))
        return
    cmd[0] = cmd[0][2:]
    cmd[-1] = cmd[-1][:-1:1]

    async def call_cc(msg, args):
        if len(args) < 1 or len(args) > 2 or args[0].lower() == 'help':
            await client.send_message(msg.channel, USAGE_TEXT)
            return

        next_chan_id = args[0]
        if not (next_chan_id.startswith('<#') and next_chan_id.endswith('>')):
            await client.send_message(msg.channel,
                                      "%s: undefined channel\n\n%s" % (next_chan_id, USAGE_TEXT))
            return
        next_chan = client.get_channel(next_chan_id[2:-1])
        if not next_chan:
            await client.send_message(msg.channel,
                                      "%s: undefined channel\n\n%s" % (args[0], USAGE_TEXT))
            return

        scrollback = deque([])
        if len(args) == 2:
            try:
                context = int(args[1])
                async for message in client.logs_from(msg.channel,
                                                    limit=min(context + 1, maxsize),
                                                    reverse=True):
                    scrollback.append("%s <%s>\t%s" % (message.timestamp.ctime(),
                                                    handle(message.author),
                                                    message.content))
                # the first message is the command that invoked us, so skip it
                scrollback.popleft()
            except ValueError:
                await client.send_message(msg.channel,
                                          "%s: cannot capture this many messages%\n\n" % (args[1], USAGE_TEXT))

        user = handle(msg.author)
        response = "invoked by %s from <#%s>" % (user, msg.channel.id)
        if len(scrollback):
            response += '\n\n' + '\n'.join(scrollback)
        await client.send_message(next_chan, response)


    if cmd[0].lower() == "call/cc":
        await call_cc(msg, cmd[1:])

client.run(secrets.BOT_TOKEN)
