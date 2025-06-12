import discord
from discord.ext import commands
from discordapp import DiscordApp
from spotifyapp import SpotifyAppOAuth, SpotifyApp
import spotipy
import os

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
        
        self.__setup_commands()
               
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
        
        elif message.content == "!ping":
            latency = self.latency * 1000  # Convert to milliseconds
            await message.channel.send(f'Pong! Latency: **{latency:.2f}ms**')
            
    def __setup_commands(self):
        '''
        Set up slash commands
        '''
        
        @self.tree.command(name="artists", description="See your most listened artists", guild=GUILD_ID)
        async def top_artists(interaction: discord.Interaction):
            """
            Get user's top listened artists
            """
            user_id = interaction.user.id

            # Check user authentication
            path = SpotifyAppOAuth.get_user_cache_path(user_id)
            notLogin = self.check_authentication(path)
            if notLogin:
                await interaction.response.send_message(embed=notLogin)
                return
            
            # Request and format data from Spotify
            auth_manager = SpotifyAppOAuth(user_id, self.client_id, self.client_secret, self.redirect_uri)
            object = SpotifyApp(auth_manager=auth_manager)
            
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
            user_id = interaction.user.id

            # Check user authentication
            path = SpotifyAppOAuth.get_user_cache_path(user_id)
            notLogin = self.check_authentication(path)
            if notLogin:
                await interaction.response.send_message(embed=notLogin)
                return
            
            # Request and format data from Spotify
            auth_manager = SpotifyAppOAuth(user_id, self.client_id, self.client_secret, self.redirect_uri)
            object = SpotifyApp(auth_manager=auth_manager)
            
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
            user_id = interaction.user.id

            # Check user authentication
            path = SpotifyAppOAuth.get_user_cache_path(user_id)
            notLogin = self.check_authentication(path)
            if notLogin:
                await interaction.response.send_message(embed=notLogin)
                return
            
            # Request and format data from Spotify
            auth_manager = SpotifyAppOAuth(user_id, self.client_id, self.client_secret, self.redirect_uri)
            object = SpotifyApp(auth_manager=auth_manager)
            
            formatted = object.format_recent(limit=50)
            formatted["author"] = self.get_user_info(interaction)

            # Convert to embed and create a pagination system
            data = DiscordApp(formatted)
            if not data.fields: # handle null data
                await interaction.response.send_message(content="You have no records", embed=data.embed)
            else:
                await data.fields_pagination(interaction=interaction, L=10)
        
        @self.tree.command(name="login", description="Log in your Spotify account", guild=GUILD_ID)
        async def login(interaction: discord.Interaction):
            await interaction.response.send_message(content="In development")
            
        # TODO: display Spotify account info
        @self.tree.command(name="logout", description="Log out your current Spotify account", guild=GUILD_ID)
        async def logout(interaction: discord.Interaction):
            user_id = interaction.user.id
            file_path = SpotifyAppOAuth.get_user_cache_path(user_id)
            
            try:
                os.remove(file_path)
                print(f"Discord user {interaction.user.name} logged out ")
            except:
                print(f"User token {user_id} not found")
            
            embed = discord.Embed(
                color=discord.Color.green(),
                description="✅ You have logged out of your Spotify account",
            )

            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="help", description="How to use FyTops", guild=GUILD_ID)
        async def help(interaction: discord.Interaction):
            await interaction.response.send_message(content="In development")
            
    def check_authentication(self, path):
        # TODO: What happen if token expired and user revoked authentication?
        embed = None
        if not os.path.exists(path):
            embed = discord.Embed(
                color=discord.Color.red(),
                title="❌ You haven't logged in to your Spotify account!",
                description="Use `/login` to authenticate FyTops to your Spotify account"
            )

        return embed 
    
    @staticmethod
    def get_user_info(interaction: discord.Interaction):
        name = interaction.user.name
        icon_url = interaction.user.display_avatar.url
        
        return {"name": name, "icon_url": icon_url}