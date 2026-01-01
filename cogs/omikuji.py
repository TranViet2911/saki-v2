import discord
from discord.ext import commands
import json
import random


def load_omikuji():
    with open("omikuji.json", "r", encoding="utf-8") as f:
        return json.load(f)


class Omikuji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="omikuji",
        description="Gieo quẻ đầu năm như chùa Nhật Bản"
    )
    async def gieoque(self, interaction: discord.Interaction):

        data = load_omikuji()

        # chọn ngẫu nhiên loại quẻ
        key = random.choice(list(data.keys()))
        quẻ = data[key]

        # chọn ngẫu nhiên lời quẻ
        message = random.choice(quẻ["messages"])

        embed = discord.Embed(
            title=f"🎐 Kết quả gieo quẻ: {quẻ['name']}",
            description=(
                f"{interaction.user.mention}\n\n"
                f"📜 **Lời quẻ:**\n{message}"
            ),
            color=quẻ["color"]
        )

        embed.set_footer(text="⛩️ Omikuji – Chúc bạn một năm bình an")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Omikuji(bot))