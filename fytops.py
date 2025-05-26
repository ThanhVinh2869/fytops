import discord
from discord.ext import commands
from discord import app_commands
from discordapp import DiscordApp
from spotifyapp import SpotifyApp

GUILD_ID = discord.Object(id=1374160501390446625)

class FyTops(commands.Bot):
    def __init__(
        self, client_id, client_secret, redirect_uri
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.spotify_object = self.get_spotify_object()
        
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
        self.setup_commands()
        
    def get_spotify_object(self):
        return SpotifyApp(self.client_id, self.client_secret, self.redirect_uri)
        
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
        
        elif message.content == "!ping":
            latency = self.latency * 1000  # Convert to milliseconds
            await message.channel.send(f'Pong! Latency: **{latency:.2f}ms**')
            
    def setup_commands(self):
        '''
        Set up slash commands
        '''
        
        @self.tree.command(
            name="artists", description="See your most listened artists", guild=GUILD_ID
        )
        async def top_artists(interaction: discord.Interaction):
            """
            Get user's top listened artists
            """
            
            # Request and format data from Spotify
            # TODO: get user Spotify account info (name, avatar) to display in description and thumbnail 
            formatted = self.spotify_object.format_top_artists(limit=50)
            formatted["description"] = f"<@{interaction.user.id}>"
            
            # Convert to embed and create a pagination system
            data = DiscordApp(formatted)
            await data.fields_pagination(interaction=interaction, L=10)

        @self.tree.command(
            name="tracks", description="See your most listened tracks", guild=GUILD_ID
        )
        async def top_tracks(interaction: discord.Interaction):
            """
            Get user's top listened artists
            """
            
            # Request and format data from Spotify
            # TODO: get user Spotify account info (name, avatar) to display in description and thumbnail 
            formatted = self.spotify_object.format_top_tracks(limit=50)
            formatted["description"] = f"<@{interaction.user.id}>"

            # Convert to embed and create a pagination system
            data = DiscordApp(formatted)
            await data.fields_pagination(interaction=interaction, L=10)

        @self.tree.command(
            name="recent", description="See your recent tracks", guild=GUILD_ID
        )
        async def recent(interaction: discord.Interaction):
            """
            Get user's recently played tracks
            """
            
            # Request and format data from Spotify
            # TODO: get user Spotify account info (name, avatar) to display in description and thumbnail 
            formatted = self.spotify_object.format_recent(limit=50)
            formatted["description"] = f"<@{interaction.user.id}>"

            # Convert to embed and create a pagination system
            data = DiscordApp(formatted)
            await data.fields_pagination(interaction=interaction, L=10)