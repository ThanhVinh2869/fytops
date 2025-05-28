import discord
from discord.ext import commands
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
        
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
        self.setup_commands()
        
    def get_user_spotify_object(self, interaction: discord.Interaction):
        return SpotifyApp(interaction.user.id, self.client_id, self.client_secret, self.redirect_uri)
        
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
        
        @self.tree.command(name="artists", description="See your most listened artists", guild=GUILD_ID)
        async def top_artists(interaction: discord.Interaction):
            """
            Get user's top listened artists
            """
            
            # Request and format data from Spotify
            object = self.get_user_spotify_object(interaction)
            formatted = object.format_top_artists(limit=50)
            formatted["author"] = self.get_user_info(interaction)
            
            # Convert to embed and create a pagination system
            data = DiscordApp(formatted)
            if not data.fields: # handle null data
                await interaction.response.send_message(content="You have no records", embed=data.embed)
            else:
                await data.fields_pagination(interaction=interaction, L=10)

        @self.tree.command(name="tracks", description="See your most listened tracks", guild=GUILD_ID)
        async def top_tracks(interaction: discord.Interaction):
            """
            Get user's top listened artists
            """
            
            # Request and format data from Spotify
            object = self.get_user_spotify_object(interaction)
            formatted = object.format_top_tracks(limit=50)
            formatted["author"] = self.get_user_info(interaction)

            # Convert to embed and create a pagination system
            data = DiscordApp(formatted)
            if not data.fields: # handle null data
                await interaction.response.send_message(content="You have no records", embed=data.embed)
            else:
                await data.fields_pagination(interaction=interaction, L=10)

        @self.tree.command(name="recent", description="See your recent tracks", guild=GUILD_ID)
        async def recent(interaction: discord.Interaction):
            """
            Get user's recently played tracks
            """
            
            # Request and format data from Spotify
            object = self.get_user_spotify_object(interaction)
            formatted = object.format_recent(limit=50)
            formatted["author"] = self.get_user_info(interaction)

            # Convert to embed and create a pagination system
            data = DiscordApp(formatted)
            if not data.fields: # handle null data
                await interaction.response.send_message(content="You have no records", embed=data.embed)
            else:
                await data.fields_pagination(interaction=interaction, L=10)
    
    @staticmethod
    def get_user_info(interaction: discord.Interaction):
        name = interaction.user.name
        icon_url = interaction.user.display_avatar.url
        
        return {"name": name, "icon_url": icon_url}