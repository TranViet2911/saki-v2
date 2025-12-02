import discord
from discord.ext import commands
import json
import random

def load_cookie():
    with open("cookie.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["cookie"]

class Cookie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="cookie", description="Bẻ một cái bánh quy may mắn")
    async def cookie(self, interaction: discord.Interaction):
        cookies = load_cookie()
        random_text = random.choice(cookies)

        await interaction.response.send_message(random_text)

async def setup(bot):
    await bot.add_cog(Cookie(bot))