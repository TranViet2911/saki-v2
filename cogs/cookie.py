import discord
from discord.ext import commands
from discord.app_commands import CommandOnCooldown
import json
import random


def load_cookie():
    with open("cookie.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["cookie"]


class Cookie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name='cookie',
        description='Bẻ một cái bánh quy lấy may hằng ngày'
    )
    @discord.app_commands.checks.cooldown(1, 43200, key=lambda i: i.user.id)
    async def cookie(self, interaction: discord.Interaction):

        cookies = load_cookie()
        random_text = random.choice(cookies)

        embed = discord.Embed(
            title="🥠 Fortune Cookie ",
            description=f"{interaction.user.mention}, bánh quy may mắn nói với bạn rằng: \n\n{random_text}",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @cookie.error
    async def cookie_cooldown(self, interaction: discord.Interaction, error):

        if isinstance(error, CommandOnCooldown):
            retry_after = int(error.retry_after)

            hours = retry_after // 3600
            mins = (retry_after % 3600) // 60

            await interaction.response.send_message(
                f"Bạn cần chờ **{hours} giờ {mins} phút** để dùng lại!",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Cookie(bot))
