from config import BOT_TOKEN

import discordapp
from discord.ext import commands

intents = discordapp.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"I'm ready!")
    
@bot.event
async def on_message(message):
    if message.content.startswith("hi"):
        await message.channel.send(f"Hello there! <@{message.author.id}>!")
        
@bot.command()
async def recent(ctx):
    await ctx.send("Requesting recent")

bot.run(BOT_TOKEN)