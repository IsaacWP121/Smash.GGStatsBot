from logging import error
from discord.ext import commands
from discord import Embed, Color
from discord_components.component import Select, SelectOption, Button
from smashGG import *
'''
get_opponents()
sets_minusdqs
opponents
games
h2hscores'''

class h2h(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    async def declare(self, ctx):
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
        self.HadToLoadMorePlayers = False
        self.HadToLoadMore = False
        self.embed = Embed(title="Head To Heads", description=f"You've competed in a total of {len(self.client.sets_minusdqs)} sets, against {len(self.client.opponents)} different players, across {len(self.client.games)} different games", color=Color.blue())
        
    async def lenChecks(self):
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


    async def edit(self, reply, embed, components=True):
        await self.lenChecks()
        if components:
            await reply.edit(content="", embed=embed, components=[
                    Select(
                        id="game_filter",
                        placeholder="Filter By Game",
                        options=[
                            SelectOption(default=i==self.game_filter or len(self.client.games)==1, label=i, value=i)
                            for i in self.temp_games
                        ]),
                    Select(
                        id="player_filter",
                        placeholder="Filter By Player", 
                        options=[
                            SelectOption(default=i==self.playerTag and i != "Load More", label=i, value = i)
                            for i in self.temp_op
                        ]),
                    Button(label = "Get H2H Results!", custom_id="get_results", style=3)])
        else:
            await reply.edit(content="", embed=embed, components=[])


    @commands.command(name="h2h")
    async def h2h(self, ctx):
        await self.declare(ctx)
        reply = await ctx.reply(embed = Embed(title="Loading", description="Please wait one moment", color=Color.blue()))
        await self.edit(reply, self.embed)

        @self.bot.event
        async def on_button_click(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.respond(
                    content=f"Only {ctx.author.mention} can interact with this."
                )
                return
            await interaction.respond(type=6)
            q = self.client.h2hscores(playerTag=self.playerTag, game=self.game_filter) # in order to reduce load times
            e = Embed(title="Head To Heads", 
                description=f"Out of {len(q)} sets against {self.playerTag}, you have won X games:", 
                color=Color.blue())
            
            for i, result in enumerate(q):
                e.add_field(name=f"Set {i+1}", value=result, inline=False)
            await self.edit(
                reply, e
                , components=False)
        
        @self.bot.event
        async def on_select_option(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.respond(
                    content=f"Only {ctx.author.mention} can interact with this."
                )
                return
            x = interaction
            await interaction.respond(type=6)
            if x.custom_id == "game_filter":
                self.game_filter = x.values[0]
                self.temp_op = None
                self.HadToLoadMorePlayers = False
                self.op = self.client.get_opponents(game=self.game_filter)
            elif x.custom_id == "player_filter":
                self.playerTag = x.values[0]
            await self.edit(reply, self.embed)
            
            

def setup(bot):
    bot.add_cog(h2h(bot))