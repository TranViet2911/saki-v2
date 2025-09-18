import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
from discord import app_commands

# Load the bot
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Setup Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Prefix and Application ID for slash command
bot = commands.Bot(command_prefix='!', intents=intents, application_id=1401895339702747156)

# Activity and Sync
@bot.event
async def on_ready():
    activity = discord.Game(name="Saki Renewed | discord.gg/vietrhythm")
    await bot.change_presence(activity=activity)

    print(f"{bot.user.name} đã được khởi động!")
    try:
        synced = await bot.tree.sync()
        print(f"Đã đồng bộ hóa {len(synced)} lệnh.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Rena gay
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Only trigger if message is exactly "rena" (case-insensitive)
    if message.content.strip().lower() == "rena":
        await message.channel.send("gay")

    await bot.process_commands(message)

# Load Cogs
async def main():
    await bot.load_extension('cogs.ping')
    await bot.load_extension('cogs.welcome')
    await bot.load_extension('cogs.afk')
    await bot.load_extension('cogs.leveling')
    await bot.load_extension('cogs.economy')
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
