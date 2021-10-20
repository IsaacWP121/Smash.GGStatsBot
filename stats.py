from logging import PlaceHolder, error, exception
from discord import client, player
from discord.ext import commands
from discord_components import DiscordComponents
from discord_components.component import Select, SelectOption, Button
from smashGG import *

class h2h(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.HadToLoadMorePlayers = False
        self.HadToLoadMore = False

    async def edit(self, reply):
        if len(self.client.games) > 25:
            if self.game_filter == "Load More":
                self.HadToLoadMore = True
                if (len(self.client.games)) < (self.client.games.index(self.temp_games[len(self.temp_games)-2])+24):
                    self.temp_games = self.client.games[
                    self.client.games.index(self.temp_games[len(self.temp_games)-2])
                                            :
                    self.client.games.index(self.temp_games[len(self.temp_games)-2])+24]
                else:
                    self.temp_games = self.client.games[
                    self.client.games.index(self.temp_games[len(self.temp_games)-2])
                                            :
                    self.client.games.index(self.temp_games[len(self.temp_games)-2])+24] + ["Load More"]
            else:
                if self.HadToLoadMore:
                    pass
                else:
                    self.temp_games = self.client.games[:24] + ["Load More"]
        
        else:
            self.temp_games = self.client.games
        
        if len(self.op) > 25:
            if self.playerTag == "Load More":
                self.HadToLoadMorePlayers = True
                if (len(self.op)) < (self.op.index(self.temp_op[len(self.temp_op)-2])+24):
                    self.temp_op = self.op[
                    self.op.index(self.temp_op[len(self.temp_op)-2])
                                            :
                    self.op.index(self.temp_op[len(self.temp_op)-2])+24]
                else:
                    self.temp_op = self.op[
                    self.op.index(self.temp_op[len(self.temp_op)-2])
                                            :
                    self.op.index(self.temp_op[len(self.temp_op)-2])+24] + ["Load More"]
            else:
                if self.HadToLoadMorePlayers:
                    pass
                else:
                    self.temp_op = self.op[:24] + ["Load More"]
        
        else:
            self.temp_op = self.op

        
        if len(self.client.games)==1:
            await reply.edit(content="Please select from the following filters!",components=[
                Select(
                    id="game_filter",
                    placeholder="Filter By Game",
                    options=[
                        SelectOption(default=True, label=i, value=i)
                        for i in self.temp_games
                    ]),
                Select(
                    id="player_filter",
                    placeholder="Filter By Player", 
                    options=[
                        SelectOption(default=i==self.playerTag and i != "Load More", label=i, value = i)
                        for i in self.temp_op
                    ]),
                Button(label = "Get H2H Results!", custom_id="get_results")])
        
        else:
            await reply.edit(content="Please select from the following filters!",components=[
                Select(
                    id="game_filter",
                    placeholder="Filter By Game",
                    options=[
                        SelectOption(default=i==self.game_filter, label=i, value=i)
                        for i in self.temp_games
                    ]),
                Select(
                    id="player_filter",
                    placeholder="Filter By Player", 
                    options=[
                        SelectOption(default=i==self.playerTag and i != "Load More", label=i, value = i)
                        for i in self.temp_op
                    ]),
                Button(label = "Get H2H Results!", custom_id="get_results")])
        
    
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
            if interaction.user.id != ctx.author.id:
                await interaction.respond(
                    content=f"Only {ctx.author.mention} can interact with this."
                )
                return
            print(self.client.h2hscores(playerTag=self.playerTag, game=self.game_filter))
            await interaction.respond(type=6)
        
        @self.bot.event
        async def on_select_option(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.respond(
                    content=f"Only {ctx.author.mention} can interact with this."
                )
                return
            if interaction.custom_id == "game_filter":
                self.game_filter = interaction.values[0]
                self.temp_op = None
                self.HadToLoadMorePlayers = False
                self.op = self.client.get_opponents(game=self.game_filter)
            elif interaction.custom_id == "player_filter":
                self.playerTag = interaction.values[0]
            await self.edit(reply)
            await interaction.respond(type=6)
            
            

def setup(bot):
    bot.add_cog(h2h(bot))