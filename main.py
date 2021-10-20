from smashGG import *
import discord, config, stats
from discord.ext import commands
from discord_components import DiscordComponents

discordBot = commands.Bot(command_prefix = "&", self_bot=False, intents=discord.Intents.all()) #initializing discord client
activity = discord.Activity(name="everyone lose their sets", type=discord.ActivityType.watching)



@discordBot.event
async def on_ready():
    DiscordComponents(discordBot)
    print("head2headbot is running")

cogs = [stats]
for i in cogs:
    i.setup(discordBot)

if __name__ == "__main__":
    discordBot.run(config.token())
    #client = smashGG(id=1572895) # either use the player id (made for testing purposes)
    client = smashGG(slug="https://smash.gg/user/d648e3d5") # or put in a smash.gg profile link
    #print(client.games)
    print(client.h2hscores("CoffeeMuncher", game="Rushdown Revolt"))