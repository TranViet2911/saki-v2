import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
from discord import app_commands

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, application_id=1401895339702747156)

@bot.event
async def on_ready():
    print(f"{bot.user.name} đã được khởi động!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Only trigger if message is exactly "rena" (case-insensitive)
    if message.content.strip().lower() == "rena":
        await message.channel.send("gay")

    await bot.process_commands(message)

async def main():
    await bot.load_extension('cogs.ping')
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())