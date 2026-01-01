import discord
from discord.ext import commands
import json
import random


def load_omikuji():
    with open("omikuji.json", "r", encoding="utf-8") as f:
        return json.load(f)


class RerollView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.button(label="🔄 Gieo lại", style=discord.ButtonStyle.primary)
    async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Bạn không thể gieo quẻ thay người khác!",
                ephemeral=True
            )
            return

        data = load_omikuji()
        key = random.choice(list(data.keys()))
        que = data[key]
        message = random.choice(que["messages"])

        embed = discord.Embed(
            title=f"🎐 Kết quả gieo quẻ: {que['name']}",
            description=(
                f"{interaction.user.mention}\n\n"
                f"📜 **Lời quẻ:**\n{message}"
            ),
            color=que["color"]
        )
        embed.set_footer(text="⛩️ Omikuji – Gieo quẻ đầu năm")

        await interaction.response.edit_message(embed=embed, view=self)


class Omikuji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="omikuji",
        description="🎐 Gieo quẻ đầu năm như chùa Nhật Bản"
    )
    async def omikuji(self, interaction: discord.Interaction):

        data = load_omikuji()
        key = random.choice(list(data.keys()))
        que = data[key]
        message = random.choice(que["messages"])

        embed = discord.Embed(
            title=f"🎐 Kết quả gieo quẻ: {que['name']}",
            description=(
                f"{interaction.user.mention}\n\n"
                f"📜 **Lời quẻ:**\n{message}"
            ),
            color=que["color"]
        )
        embed.set_footer(text="⛩️ Omikuji – Chúc bạn một năm bình an")

        view = RerollView(interaction.user.id)

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Omikuji(bot))
