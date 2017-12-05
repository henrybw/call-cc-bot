import discord
from collections import deque
from sys import maxsize
import secrets

client = discord.Client()

USAGE_TEXT = ("usage: `~(call/cc #channel [context])`\n\n"
              "~~call~~ continue the current ~~continuation~~ conversation in another "
              "channel on this server, where `context` is the number of previous "
              "messages to repost (0, by default).")

def id_from_user(author):
    return "<@%s>" % author.id

def id_from_channel(chan):
    return "<#%s>" % chan.id

# discord ids are surrounded with '<X' and '>' markers (X is, e.g., '#' for
# channels and '@' for users) to denote that they are ids of some sort.
def deformat_id(fmt_id):
    return fmt_id[2:-1]

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

    def strip_sexps(cmd):
        cmd[0] = cmd[0][2:]
        cmd[-1] = cmd[-1][:-1:1]
    strip_sexps(cmd)

    def compress_spaces(cmd):
        return ' '.join(cmd).split()
    cmd = compress_spaces(cmd)

    async def call_cc(msg, args):
        if len(args) < 1 or len(args) > 2 or args[0].lower() == 'help':
            print(args)
            await client.send_message(msg.channel, USAGE_TEXT)
            return

        next_chan_id = args[0]
        if not (next_chan_id.startswith('<#') and next_chan_id.endswith('>')):
            await client.send_message(msg.channel,
                                      "%s: undefined channel\n\n%s" % (next_chan_id, USAGE_TEXT))
            return
        next_chan = client.get_channel(deformat_id(next_chan_id))
        if not next_chan:
            await client.send_message(msg.channel,
                                      "%s: undefined channel\n\n%s" % (next_chan_id, USAGE_TEXT))
            return

        scrollback = deque([])
        if len(args) == 2:
            try:
                context = int(args[1])
                if context < 0:
                    await client.send_message(msg.channel,
                                              ("cannot capture messages from the future: "
                                               "time manipulation not yet supported\n\n%s" % (USAGE_TEXT,)))
                    return

                async for message in client.logs_from(msg.channel,
                                                      limit=min(context + 1, maxsize),
                                                      reverse=True):
                    scrollback.append("%s <%s>\t%s" % (message.timestamp.ctime(),
                                                       id_from_user(message.author),
                                                       message.content))
                # the first message is the command that invoked us, so skip it
                scrollback.popleft()
            except ValueError:
                await client.send_message(msg.channel,
                                          "%s: cannot capture this many messages\n\n%s" % (args[1], USAGE_TEXT))
                raise

        response = "invoked by %s from %s" % (id_from_user(msg.author), id_from_channel(msg.channel))
        if len(scrollback):
            response += '\n\n' + '\n'.join(scrollback)

        try:
            await client.send_message(next_chan, response)
        except discord.errors.HTTPException:
            await client.send_message(msg.channel,
                                      ("discord got mad at me. it's probably not your fault, "
                                       "but here's the usage documentation anyway (y'know, in "
                                       "case it *is* actually your fault...):\n\n%s" % (USAGE_TEXT,)))
            raise

    if cmd[0].lower() == "call/cc":
        await call_cc(msg, cmd[1:])

client.run(secrets.BOT_TOKEN)
