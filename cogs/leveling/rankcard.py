import discord
from discord.ext import commands
import io
from PIL import Image, ImageDraw, ImageFont
from .db import get_user, LEVEL_UP_MULTIPLIER

class LevelRankCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="rank", description="Show your rank card")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = get_user(member.id)

        if not user:
            return await interaction.response.send_message(f"{member.mention} hasn’t started gaining XP yet!")

        xp, level = user[1], user[2]
        xp_needed = level * LEVEL_UP_MULTIPLIER

        card_width, card_height = 600, 200
        img = Image.new("RGB", (card_width, card_height), (30, 30, 30))
        draw = ImageDraw.Draw(img)

        try:
            font_large = ImageFont.truetype("arial.ttf", 30)
            font_small = ImageFont.truetype("arial.ttf", 20)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        avatar_bytes = await member.display_avatar.read()
        avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((128, 128))

        mask = Image.new("L", (128, 128), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 128, 128), fill=255)
        img.paste(avatar_img, (30, 36), mask)

        draw.text((180, 40), member.name, font=font_large, fill=(255, 255, 255))
        draw.text((180, 80), f"Level: {level}", font=font_small, fill=(255, 215, 0))
        draw.text((180, 105), f"XP: {xp}/{xp_needed}", font=font_small, fill=(173, 216, 230))

        bar_x, bar_y, bar_width, bar_height = 180, 140, 370, 30
        progress = int((xp / xp_needed) * bar_width) if xp_needed > 0 else 0
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(50, 50, 50))
        draw.rectangle([bar_x, bar_y, bar_x + progress, bar_y + bar_height], fill=(0, 176, 244))

        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        buffer.seek(0)

        file = discord.File(buffer, filename="rank.png")
        await interaction.response.send_message(file=file)