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
            print(f"Synced {len(synced)} commands to guild {GUILD_ID}")
        
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
        @self.tree.command(
            name="recent", 
            description="Get recent tracks",
            guild=GUILD_ID
        )
        async def recent(interaction: discord.Interaction, limit: int, optional: int=None):
            '''
            '''
            await interaction.response.send_message(f"Requesting not recent {limit} {optional}")