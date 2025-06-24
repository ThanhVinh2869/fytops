import discord
from discord.ext import commands
from discordapp import DiscordApp
from spotifyapp import SpotifyAppOAuth, SpotifyApp
import spotipy
import os
from urllib.parse import urlparse, parse_qs

GUILD_ID = discord.Object(id=1374160501390446625)

class FyTops(commands.Bot):
    def __init__(self, client_id, client_secret, redirect_uri):
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
        async def __command_call(command, interaction, time_range):
            user_id = interaction.user.id

            # Check user authentication
            notLogin = self.check_authentication(user_id)
            if notLogin:
                await interaction.response.send_message(embed=notLogin)
                return
            
            # Request and format data from Spotify
            auth_manager = self.__create_auth_manager(user_id)
            object = SpotifyApp(auth_manager=auth_manager)
            
            commands_map = {
                "artists": object.format_top_artists,
                "tracks": object.format_top_tracks,
                "recent": object.format_recent
            }
            
            try:
                formatted = commands_map[command](limit=50, time_range=time_range)
            except:
                formatted = commands_map[command](limit=50)
            formatted["author"] = self.get_discord_user(interaction)
            
            # Convert to embed and create a pagination system
            data = DiscordApp(formatted)
            await data.fields_pagination(interaction=interaction, L=10)

        @self.tree.command(name="artists", description="See your most listened artists", guild=GUILD_ID)
        @discord.app_commands.describe(time_range="Over what time frame the data are computed")
        async def top_artists(interaction: discord.Interaction, time_range: str="medium_term"):
            """
            Get user's top listened artists
            """
            await __command_call("artists", interaction, time_range)

        @self.tree.command(name="tracks", description="See your most listened tracks", guild=GUILD_ID)
        @discord.app_commands.describe(time_range="Over what time frame the data are computed")
        async def top_tracks(interaction: discord.Interaction, time_range: str="medium_term"):
            """
            Get user's top listened tracks
            """
            await __command_call("tracks", interaction, time_range)

        @self.tree.command(name="recent", description="See your recent tracks", guild=GUILD_ID)
        async def recent(interaction: discord.Interaction):
            """
            Get user's recently played tracks
            """
            await __command_call("recent", interaction, "medium_term")      
        
        @self.tree.command(name="login", description="Log in your Spotify account", guild=GUILD_ID)
        async def login(interaction: discord.Interaction):
            user_id = interaction.user.id

            embed = discord.Embed(
                color=discord.Color.green(),
                description="✅ You have already logged in!"
            )
            
            notLogin = self.check_authentication(user_id)
            if notLogin:
                auth_manager = self.__create_auth_manager(user_id)
                auth_url = auth_manager.get_authorize_url()
                embed = discord.Embed(
                    color=discord.Color.yellow(),
                    description=f"Click [here]({auth_url}) to link your Spotify account with the current Discord account"
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        @self.tree.command(name="auth", description="Provide authentication code", guild=GUILD_ID)
        async def auth(interaction: discord.Interaction, code: str):
            user_id = interaction.user.id
            auth_manager = self.__create_auth_manager(user_id)
            
            notLogin = self.check_authentication(user_id)
            if notLogin:
                # Retrieve the auth code
                try:
                    parsed_url = urlparse(code)
                    query_params = parse_qs(parsed_url.query)
                    auth_code = query_params.get('code')[0]
                except: # if failed to parse the query then try using the original content
                    auth_code = code
                
                # Exchange auth code for token
                try:
                    auth_manager.get_access_token(code=auth_code, as_dict=False)
                except spotipy.exceptions.SpotifyOauthError as e:
                    print(f"Token exchange error: {e}")
                    embed = discord.Embed(
                        color=discord.Color.red(),
                        description="❌ Invalid authorization code, please try again!"
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

            # Get Spotify account info
            object = SpotifyApp(auth_manager=auth_manager)
            description, icon_url = object.spotify_user_info()
              
            embed = discord.Embed(
                color=discord.Color.green(),
                title="✅ You have successfully logged in as",
                description=description,
            )
            
            embed.set_thumbnail(url=icon_url)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        # TODO: display Spotify account info
        @self.tree.command(name="logout", description="Log out your current Spotify account", guild=GUILD_ID)
        async def logout(interaction: discord.Interaction):
            user_id = interaction.user.id
                        
            embed = discord.Embed(
                color=discord.Color.green(),
                description="✅ You have logged out of your Spotify account",
            )
            
            try:
                os.remove(SpotifyAppOAuth.get_user_cache_path(user_id))
                print(f"Discord user {interaction.user.name} logged out")
            except:
                print(f"User token {user_id} not found, sent default logout message")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        @self.tree.command(name="help", description="How to use FyTops", guild=GUILD_ID)
        async def help(interaction: discord.Interaction):
            await interaction.response.send_message(content="In development")
            
    def check_authentication(self, user_id):
        path = SpotifyAppOAuth.get_user_cache_path(user_id)

        embed = discord.Embed(
            color=discord.Color.red(),
            title="❌ You haven't logged in to your Spotify account!",
            description="Use `/login` to authenticate FyTops to your Spotify account"
        )
        
        if os.path.exists(path):
            try:
                auth_manager = self.__create_auth_manager(user_id)
                object = SpotifyApp(auth_manager=auth_manager)
                object.me()
                embed = None # clear error message if token is valid
            # Refresh token invalid because user revoked authentication
            except spotipy.SpotifyOauthError as e:
                print(f"Authentication Error: {e}")
                os.remove(path)
                print(f"Removed invalid token {user_id}")

        return embed
    
    def __create_auth_manager(self, user_id):
        return SpotifyAppOAuth(user_id, self.client_id, self.client_secret, self.redirect_uri)
    
    @staticmethod
    def get_discord_user(interaction: discord.Interaction):
        name = interaction.user.name
        icon_url = interaction.user.display_avatar.url
        
        return {"name": name, "icon_url": icon_url}