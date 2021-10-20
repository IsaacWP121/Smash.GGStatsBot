from logging import PlaceHolder, error, exception
from discord import client, player
from discord.ext import commands
from discord_components import DiscordComponents
from discord_components.component import Select, SelectOption
from smashGG import *

class h2h(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    async def edit(self, reply):

        if len(self.op) > 25:
            temp_op = self.op[:24] + ["Load More"]
        else:
            temp_op = self.op
        if len(self.client.games) > 25:
            temp_games = self.client.games[:24] + ["Load More"]
        else:
            temp_games = self.client.games
        
        if len(self.client.games)==1:
            await reply.edit(components=[
                Select(
                    id="game_filter",
                    placeholder="Filter By Game",
                    options=[
                        SelectOption(default=True, label=i, value=i)
                        for i in temp_games
                    ]),
                Select(
                    id="player_filter",
                    placeholder="Filter By Player", 
                    options=[
                        SelectOption(default=i==self.playerTag, label=i, value = i)
                        for i in temp_op
                    ])])
        else:
            await reply.edit(components=[
                Select(
                    id="game_filter",
                    placeholder="Filter By Game",
                    options=[
                        SelectOption(default=i==self.game_filter, label=i, value=i)
                        for i in temp_games
                    ]),
                Select(
                    id="player_filter",
                    placeholder="Filter By Player", 
                    options=[
                        SelectOption(default=i==self.playerTag, label=i, value = i)
                        for i in temp_op
                    ])])

    
    @commands.command(name="h2h")
    async def h2h(self, ctx):
        try:
            if "smash.gg/user/" in ctx.message.content.split()[1]:
                self.client = smashGG(slug=ctx.message.content.split()[1])
            elif ctx.message.content.split()[1].isnumeric():
                self.client = smashGG(id=int(ctx.message.content.split()[1]))
            else:
                await ctx.reply(f"The correct syntax of {ctx.prefix}h2h is {ctx.prefix}h2h https://smash.gg/user/userDescriminator")
        except error as e:
            print(e)
        
        self.playerTag = None
        self.game_filter = "Both"
        self.op = self.client.get_opponents(game=self.game_filter)
        reply = await ctx.reply("Loading, one moment please")
        await self.edit(reply)
        

        @self.bot.event
        async def on_button_click(interaction):

            await self.edit(reply)
            await interaction.respnd(type=6)
        
        @self.bot.event
        async def on_select_option(interaction):
            if interaction.custom_id == "game_filter":
                self.game_filter = interaction.values[0]
                self.op = self.client.get_opponents(game=self.game_filter)
            elif interaction.custom_id == "player_filter":
                self.playerTag = interaction.values[0]
                print(self.client.h2hscores(playerTag=self.playerTag, game=self.game_filter))
            await self.edit(reply)
            await interaction.respond(type=6)
            
            

def setup(bot):
    bot.add_cog(h2h(bot))