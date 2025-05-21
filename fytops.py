import discord
from discord.ext import commands
from discord import app_commands

GUILD_ID = discord.Object(id=1374160501390446625)

class FyTops(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents)
        self.setup_commands()

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        
        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} commands to guild {GUILD_ID.id}")
        
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_message(self, message):
        if message.author == self.user:
            return 
        
        if message.content.startswith("hi"):
            await message.channel.send(f"Hi there! <@{message.author.id}>!")
            
    def setup_commands(self):
        '''
        Set up slash commands
        '''
        
        @self.tree.command(name="artists", description="See your most listened artists", guild=GUILD_ID)
        @app_commands.describe(
            limit = "the number of entities to return (max 50)",
            offset = "the index of the first entity to return",
            time_range = "Over what time frame are the stats computed (short, medium, long)"
        )
        async def top_artists(interaction: discord.Interaction, limit: int = 20, offset: int = 0, time_range: str = 'm'):
            """Get user's top listened artists
                
                Parameters:
                    limit (int): the number of entities to return (max 50)
                    offset (int): the index of the first entity to return
                    time_range (str): Over what time frame are the affinities computed
                    Valid-values: short, medium, long
            """
            
            # TODO: Hook Spotify call function
            await interaction.response.send_message(f"Requesting {limit} top artists...")




        @self.tree.command(name="tracks", description="See your most listened tracks", guild=GUILD_ID)
        @app_commands.describe(
            limit = "the number of entities to return (max 50)",
            offset = "the index of the first entity to return",
            time_range = "Over what time frame are the stats computed (short, medium, long)"
        )
        async def top_tracks(interaction: discord.Interaction, limit: int = 20, offset: int = 0, time_range: str = 'm'):
            """Get user's top listened artists
                
                Parameters:
                    limit (int): the number of entities to return (max 50)
                    offset (int): the index of the first entity to return
                    time_range (str): Over what time frame are the affinities computed
                    Valid-values: short, medium, long
            """
            
            # TODO: Hook Spotify call function
            await interaction.response.send_message(f"Requesting {limit} top tracks...")




        @self.tree.command(name="recent", description="See your recent tracks", guild=GUILD_ID)
        @app_commands.describe(
            limit = "number of tracks (max 50)"
        )
        async def recent(interaction: discord.Interaction, limit: int = 20):
            """Get user's recently played tracks
            
                Parameters:
                    - limit - the number of entities to return (max 50)
            """
            
            # TODO: Hook Spotify call function
            await interaction.response.send_message(f"Requesting {limit} recent tracks...")