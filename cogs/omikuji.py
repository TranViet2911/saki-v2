import discord
from discord.ext import commands
import json
import random


def load_omikuji():
    with open("omikuji.json", "r", encoding="utf-8") as f:
        return json.load(f)


class OmikujiView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=60)  # nút tồn tại 60s
        self.user = user

    @discord.ui.button(label="🔁 Gieo lại", style=discord.ButtonStyle.primary)
    async def reroll(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        # chỉ cho người đã gieo quẻ dùng
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ Bạn không phải người đã gieo quẻ này!",
                ephemeral=True
            )
            return

        data = load_omikuji()

        key = random.choice(list(data.keys()))
        quẻ = data[key]
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

        await interaction.response.edit_message(embed=embed, view=self)


class Omikuji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="gieoque",
        description="Gieo quẻ đầu năm như chùa Nhật Bản"
    )
    async def gieoque(self, interaction: discord.Interaction):

        data = load_omikuji()

        key = random.choice(list(data.keys()))
        quẻ = data[key]
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

        view = OmikujiView(interaction.user)

        await interaction.response.send_message(
            embed=embed,
            view=view
        )


async def setup(bot):
    await bot.add_cog(Omikuji(bot))
