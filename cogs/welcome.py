import discord
from discord.ext import commands
import os
from easy_pil import Editor, load_image_async, font
from io import BytesIO

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
@commands.Cog.listener()
async def on_member_join(self, member: discord.Member):
    # --- CONFIG ---
    channel_id = 1240680129714196520
    image_filename = "image.png"

    # --- Channel check ---
    welcome_channel = member.guild.get_channel(channel_id)
    if not welcome_channel:
        print(f"[ERROR] Channel ID {channel_id} not found in guild {member.guild.name}.")
        return

    # --- Image check ---
    image_path = f"./cogs/image/{image_filename}"
    if not os.path.exists(image_path):
        print(f"[ERROR] Image {image_path} not found.")
        return

    try:
        print(f"[DEBUG] Member joined: {member.name}")

        # --- Avatar processing ---
        avatar_url = str(member.avatar.url)
        avatar_image = await load_image_async(avatar_url)
        avatar = Editor(avatar_image).resize((250, 250)).circle_image()

        # --- Background processing ---
        bg = Editor(image_path)

        # --- Fonts ---
        try:
            font_big = font.load_default(size=90, variant="bold")
            font_small = font.load_default(size=60, variant="bold")
        except Exception as e:
            print("[WARNING] Poppins font not available, using default EasyPil font.")
            font_big = font.load_default()
            font_small = font.load_default()

        # --- Compose image ---
        bg.paste(avatar, (835, 340))
        bg.ellipse((835, 340), 250, 250, outline="white", stroke_width=5)
        bg.text((960, 620), f"Welcome to {member.guild.name}!", color="white", font=font_big, align="center")
        bg.text((960, 740), f"{member.name} is member #{member.guild.member_count}!", color="white", font=font_small, align="center")

        # --- Save image to BytesIO ---
        image_bytes = BytesIO()
        bg.image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        bg_file = discord.File(fp=image_bytes, filename=image_filename)

        # --- Send message and image ---
        await welcome_channel.send(f"Thanks for joining {member.guild.name}, {member.name}!")
        await welcome_channel.send(file=bg_file)
        print(f"[DEBUG] Welcome image sent for {member.name} in {welcome_channel.name}")

    except Exception as e:
        print("[ERROR] Exception in welcome cog:", e)
        
async def setup(bot):
    await bot.add_cog(Welcome(bot))