import discord
from discord.ext import commands
from discordapp import DiscordApp
from spotifyapp import SpotifyAppOAuth, SpotifyApp
import spotipy
import os
from urllib.parse import urlparse, parse_qs
from loggerFyTops import logger

GUILD_ID = discord.Object(id=1374160501390446625)

class FyTops(commands.Bot):
    """A Discord Bot to display user's Spotify account data"""
    
    def __init__(self, client_id, client_secret, redirect_uri):
        """
        Create an instance of Discord bot FyTops

        Attributes
        ---
        client_id:
            Must be supplied or set as environment variable
        client_secret:
            Must be supplied or set as environment variable
        redirect_uri:
            Must be supplied or set as environment variable
        """
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
        self.__setup_commands()
               
    async def on_ready(self):
        logger.info(f"Logged on Discord as {self.user}")

        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            logger.info(f"Synced {len(synced)} commands to guild {GUILD_ID.id}")
        
        except Exception as e:
            logger.error(f"Error syncing commands: {e}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return 
        
        elif message.content == "!ping":
            latency = self.latency * 1000  # Convert to milliseconds
            await message.channel.send(f'Pong! Latency: **{latency:.2f}ms**')
            
    def __setup_commands(self):
        """Set up slash commands"""
        
        async def __command_call(command: str, interaction: discord.Interaction, time_range: str):
            """Calling appropriate commands to request API calls

            Parameters
            ---
            command: :class:`str`
                "artists": get user's top listened artists  
                "tracks": get user's top listened tracks  
                "recent": get user's recently played tracks
            interaction: :class:`discord.Interaction` 
                current interaction from Discord
            time_range: :class:`str`
                short, medium, or long (can abbreviate)
            """
            
            user_id = interaction.user.id
            
            logger.info(f"{user_id}: User requesting /{command}")

            # Check user authentication
            notLogin = self.check_authentication(user_id)
            if notLogin:
                await interaction.response.send_message(embed=notLogin)
                logger.warning(f"{user_id}: Unable to proceed request due to unexisted or invalid access token")
                return
            
            # Request and format data from Spotify
            auth_manager = self.__create_auth_manager(user_id)
            object = SpotifyApp(auth_manager=auth_manager)
            
            commands_map = {
                "artists": object.format_top_artists,
                "tracks": object.format_top_tracks,
                "recent": object.format_recent
            }
            
            # Call appropriate request and convert data to standard format
            # /recent does not accept parameter "time_range"
            try:
                formatted = commands_map[command](limit=50, time_range=time_range)
            except:
                formatted = commands_map[command](limit=50)
            formatted["author"] = self.get_discord_user(interaction)
            
            # Convert to embed and create a pagination system
            data = DiscordApp(formatted)
            await data.fields_pagination(interaction=interaction, L=10)
            logger.info(f"{user_id}: Successfully returned API call request")

        @self.tree.command(name="artists", description="See your most listened artists", guild=GUILD_ID)
        @discord.app_commands.describe(time_range="Over what time frame the data are computed")
        async def top_artists(interaction: discord.Interaction, time_range: str="medium_term"):       
            await __command_call("artists", interaction, time_range)

        @self.tree.command(name="tracks", description="See your most listened tracks", guild=GUILD_ID)
        @discord.app_commands.describe(time_range="Over what time frame the data are computed")
        async def top_tracks(interaction: discord.Interaction, time_range: str="medium_term"):
            await __command_call("tracks", interaction, time_range)

        @self.tree.command(name="recent", description="See your recent tracks", guild=GUILD_ID)
        async def recent(interaction: discord.Interaction):
            await __command_call("recent", interaction, "none")      
        
        
        @self.tree.command(name="login", description="Log in your Spotify account", guild=GUILD_ID)
        async def login(interaction: discord.Interaction):
            """Check Spotify account login information"""
            
            user_id = interaction.user.id

            embed = discord.Embed(
                color=discord.Color.green(),
                description="✅ You have already logged in!"
            )
            
            # Send authorization link if not logged in
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
            """Manually retrieve authorization code from user"""
            
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
                    logger.error(f"Token exchange error: {e}")
                    embed = discord.Embed(
                        color=discord.Color.red(),
                        description="❌ Invalid authorization code, please try again!"
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

            # Get Spotify account info if authentication successful
            object = SpotifyApp(auth_manager=auth_manager)
            description = object.user_info["description"].splitlines()[0]
            thumbnail = object.user_info["thumbnail"]
              
            # Construct embed message
            embed = discord.Embed(
                color=discord.Color.green(),
                title="✅ You have successfully logged in as",
                description=description,
            )
            
            embed.set_thumbnail(url=thumbnail)
            
            logger.info(f"{user_id}: Valid authorization code, access token successfully created")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        @self.tree.command(name="logout", description="Log out your current Spotify account", guild=GUILD_ID)
        async def logout(interaction: discord.Interaction):
            """Remove Spotify account linkage with current Discord user"""
            
            user_id = interaction.user.id
                        
            embed = discord.Embed(
                color=discord.Color.green(),
                description="✅ You have logged out of your Spotify account",
            )
            
            try:
                os.remove(SpotifyAppOAuth.get_user_cache_path(user_id))
            except:
                pass
        
            logger.debug(f"{user_id}: Logged out Spotify account, access token removed")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @self.tree.command(name="help", description="How to use FyTops", guild=GUILD_ID)
        async def help(interaction: discord.Interaction):
            menu ='''     
Hello, my name is **FyTops**, I am a bot developed by <@1181768796592156712> to help you access statistics of your Spotify account.

**Available commands**
`/artists <time_range>`: Show a list of your most listened Spotify artists.
`/tracks <time_range>`: Show a list of your most listened Spotify tracks.
`/recent`: Show your most recently listened tracks on Spotify.

**Optional parameter**
`<time_range>`: Set to `medium` by default, can be `short` (30 days), `medium` (6 months), or `long` (12 months). 
'''

            embed = discord.Embed(
                color=discord.Colour.orange(),
                description=menu
            )
            
            await interaction.response.send_message(embed=embed)
            
    def check_authentication(self, user_id: int) -> str: 
        """
        Check if Discord user has connected to a Spotify account

        Attributes
        ---
        user_id: :class:`int`
            Discord id of the current user

        Returns
        ---
        :class:`str` 
            return an embed message if cannot find a valid Spotify access token, 
            return an empty string otherwise
        """
        
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
                logger.debug(f"{user_id}: Authentication validated, user access token valid")
            
            # Refresh token invalid - user revoked authentication
            except spotipy.SpotifyOauthError as e:
                os.remove(path)
                logger.warning(f"{user_id}: Invalid acccess token due to user revoked app permission")

        return embed
    
    def __create_auth_manager(self, user_id):
        return SpotifyAppOAuth(user_id, self.client_id, self.client_secret, self.redirect_uri)
    
    @staticmethod
    def get_discord_user(interaction: discord.Interaction):
        name = interaction.user.name
        icon_url = interaction.user.display_avatar.url
        
        return {"name": name, "icon_url": icon_url}