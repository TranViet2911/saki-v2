# Import
import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Prefix Command
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} đã được khởi động!")
    
# Load Cogs
bot.load_extensions('cogs.ping')

# Rena gay :)
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
		
	if "rena" in message.content.lower():
		await message.channel.send(f"gay")
	
	await bot.process_commands(message)
bot.run(token)
