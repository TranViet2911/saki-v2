import discord
from discord.ext import commands
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from .database import get_user, LEVEL_UP_MULTIPLIER, get_top_users, get_global_boost, get_user_boost, get_role_boost, get_temp_boost

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

        # Get rank position
        all_users = [row[0] for row in get_top_users(9999)]
        rank_pos = all_users.index(member.id) + 1 if member.id in all_users else "N/A"
        total_users = len(all_users)

        # Calculate boost multiplier
        boost_mult = get_global_boost() * get_user_boost(member.id) * get_temp_boost(member.id)
        for role in member.roles:
            boost_mult *= get_role_boost(role.id)

        # -------------------------------
        # Create Image
        # -------------------------------
        card_width, card_height = 750, 250
        img = Image.new("RGB", (card_width, card_height), (25, 25, 25))
        draw = ImageDraw.Draw(img)

        # Gradient background
        for y in range(card_height):
            r = int(40 + (100 - 40) * (y / card_height))
            g = int(30 + (60 - 30) * (y / card_height))
            b = int(60 + (140 - 60) * (y / card_height))
            draw.line([(0, y), (card_width, y)], fill=(r, g, b))

        # Avatar with glow
        avatar_bytes = await member.display_avatar.read()
        avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((150, 150))

        mask = Image.new("L", (150, 150), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 150, 150), fill=255)

        glow = Image.new("RGBA", (170, 170), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse((0, 0, 170, 170), fill=(0, 176, 244, 120))
        glow = glow.filter(ImageFilter.GaussianBlur(12))
        img.paste(glow, (25, 40), glow)
        img.paste(avatar_img, (35, 50), mask)

        # Fonts (use a better .ttf if available in your project folder)
        try:
            font_big = ImageFont.truetype("arialbd.ttf", 40)   # bold username
            font_med = ImageFont.truetype("arial.ttf", 28)     # level / rank
            font_small = ImageFont.truetype("arial.ttf", 24)   # XP / multiplier
        except:
            font_big = ImageFont.load_default()
            font_med = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Username
        draw.text((220, 50), member.name, font=font_big, fill=(255, 255, 255))

        # Level & Rank
        draw.text((220, 100), f"⭐ Level {level}", font=font_med, fill=(255, 215, 0))
        draw.text((220, 140), f"🏆 Rank #{rank_pos}/{total_users}", font=font_med, fill=(173, 216, 230))

        # Progress bar
        bar_x, bar_y, bar_width, bar_height = 220, 180, 480, 35
        progress = int((xp / xp_needed) * bar_width) if xp_needed > 0 else 0

        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                               radius=18, fill=(50, 50, 50))
        progress_bar = Image.new("RGBA", (progress, bar_height), (0, 176, 244, 255))
        progress_bar = progress_bar.filter(ImageFilter.GaussianBlur(1))
        img.paste(progress_bar, (bar_x, bar_y), progress_bar)

        # XP Text
        draw.text((bar_x, bar_y - 30), f"XP: {xp}/{xp_needed}", font=font_small, fill=(230, 230, 230))

        # Multiplier
        draw.text((bar_x, bar_y + 45), f"⚡ Multiplier: x{boost_mult:.2f}", font=font_small, fill=(200, 180, 255))

        # Export
        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        buffer.seek(0)

        file = discord.File(buffer, filename="rank.png")
        await interaction.response.send_message(file=file)
