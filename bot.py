import discord
from discord.ext import commands
import SelfIDs
import cogs.utils.prefix as Prefix
import cogs.emojis as Emojis
import os.path
import json
import datetime

startup_extensions = [
    "cogs.fun",
    "cogs.eval",
    "cogs.gens",
    "cogs.botinfos",
    "cogs.hepbot",
    "cogs.ack",
    "cogs.bgt",
    "cogs.clear",
    "cogs.serverinfo",
    "cogs.count",
    "cogs.mute",
    "cogs.discrim",
    "cogs.guildlogs"
]

cDir = os.path.dirname(os.path.abspath(__file__))
muteListDir = f"{cDir}/muteList.json"

try:
    with open(muteListDir, "r") as f:
        pass
except FileNotFoundError:
    print("Mute List not made. Creating...")
    with open(muteListDir, "a+") as f:
        json.dump({}, f)
    print("muteList.json created.")

prefixes = Prefix.prefixes
bot = commands.Bot(command_prefix=prefixes, description="A Self Bot", max_messages=1000, self_bot=True)
bot.remove_command("help")
bot.blank = "\u200B"
bot.muteListDir = muteListDir
bot.ready = False


# bot.muteList = muteList
# bot.muteListFile = muteListFile

def emojireplacetext(message):
    if not message: return
    try:
        output = message.content
    except AttributeError:
        print(f"discord.Message obj needed. {type(message)} was given.")
        return

    for emoji in Emojis.emojis:
        if f"[{emoji}]" in output.lower():
            fEmoji = Emojis.emojis[emoji]
            output = output.replace(f"[{emoji}]", fEmoji)

    return output


@bot.event
async def on_ready():
    gamename = "with Orangutans \U0001f435"
    await bot.change_presence(game=discord.Game(name=gamename))
    print("Logged in as:")
    print("Name: " + str(bot.user))
    print("ID: " + str(bot.user.id))
    print("Playing", gamename)
    print("Prefixes: " + Prefix.Prefix())
    bot.ready = True


@bot.event
async def on_message(message):
    if message.author.id != bot.user.id:
        return
    if not bot.ready:
        for prefix in prefixes:
            if message.content.startswith(prefix):
                await message.channel.send("I am still loading.")
                return
    if "[" in message.content:
        if "`" not in message.content and "\u200B" not in message.content:
            await message.edit(content=(emojireplacetext(message)))
    if "Nihaal" in message.content:
        await message.edit(content=message.content.replace("Nihaal", "*****"))
    await bot.process_commands(message)


@bot.event
async def on_message_edit(before, after):
    if after.author.id != bot.user.id:
        return
    if "[" in after.content:
        if not "```" in after.content:
            await after.edit(content=(emojireplacetext(after)))
    await bot.process_commands(after)


@bot.event
async def on_guild_remove(guild):
    embed = discord.Embed(description=f"<@{bot.user.id}> left the guild {guild.name}")
    embed.add_field(name="Owner", value=f"{str(guild.owner)} ({guild.owner.id}) <@{guild.owner.id}>")
    embed.set_footer(text=("Server left on " + datetime.datetime.utcnow().strftime("%A %d %B %Y at %H:%M:%S")))

    if guild.icon_url:
        embed.set_image(url=guild.icon_url)
        embed.add_field(name="Server Icon URL", value=guild.icon_url)

    await bot.get_channel(304597561615056899).send(embed=embed)


@bot.command()
async def load(ctx, extension_name: str):
    """Loads a module."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send(bot.blank + "```py\n{}: {}\n```".format(type(e).__name__, str(e)), delete_after=3)
        return
    await ctx.send(bot.blank + "{} loaded.".format(extension_name), delete_after=3)


@bot.command()
async def unload(ctx, extension_name: str):
    """Unloads a module"""
    bot.unload_extension(extension_name)
    await ctx.send(bot.blank + "{} unloaded.".format(extension_name), delete_after=3)

@bot.command(name="reload")
async def _reload(ctx, *, module: str):
    """Reloads a module."""
    try:
        bot.unload_extension(module)
        bot.load_extension(module)
    except Exception as e:
        await ctx.send("{}: {}".format(type(e).__name__, e))
    else:
        await ctx.send(":thumbsup:")


@bot.command()
async def shutdown(ctx):
    """Shutdown"""
    try:
        await ctx.send("System Shutting down.")
        await bot.logout()
        await bot.close()
    except:
        await ctx.send("Error!")


@bot.command()
async def shutdownall(ctx):
    prefixes = [
        "o!",
        "q!",
        "t!",
        "v!",
        "s."
    ]
    for bot in prefixes:
        await ctx.send(f"{bot}shutdown")


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print("Failed to load extension {}\n{}".format(extension, exc))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        print(error)
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("`{}` is not a valid command".format(ctx.invoked_with))
    elif isinstance(error, commands.errors.CommandInvokeError):
        print(error)
    else:
        print(error)


bot.run(SelfIDs.token, bot=False)
