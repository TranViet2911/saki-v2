import discord
from discord.ext import commands
from discord import app_commands
import os
from easy_pil import Editor, load_image_async, Font
from io import BytesIO

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.send_welcome(member)

    # ✅ Slash command with app_commands
    @app_commands.command(name="testwelcome", description="Test the welcome message & image.")
    @app_commands.checks.has_permissions(administrator=True)
    async def test_welcome(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await self.send_welcome(member, channel=interaction.channel)
        await interaction.response.send_message(
            f"✅ Test welcome sent for {member.mention}", ephemeral=True
        )

    # ✅ Shared function
    async def send_welcome(self, member: discord.Member, channel: discord.TextChannel = None):
        channel_id = 1240680129714196520
        image_filename = "image.png"

        welcome_channel = channel or member.guild.get_channel(channel_id)
        if not welcome_channel:
            print(f"[ERROR] Channel ID {channel_id} not found in guild {member.guild.name}.")
            return

        image_path = f"./cogs/image/{image_filename}"
        if not os.path.exists(image_path):
            print(f"[ERROR] Image {image_path} not found.")
            return

        try:
            avatar_url = str(member.display_avatar.url)
            avatar_image = await load_image_async(avatar_url)
            avatar = Editor(avatar_image).resize((250, 250)).circle_image()

            bg = Editor(image_path)

            try:
                font_big = Font.poppins(size=90, variant="bold")
                font_small = Font.poppins(size=60, variant="bold")
            except Exception:
                font_big = Font.default(size=90)
                font_small = Font.default(size=60)

            bg.paste(avatar, (835, 340))
            bg.ellipse((835, 340), 250, 250, outline="white", stroke_width=5)
            bg.text((960, 620), f"Welcome to the server!", color="white", font=font_big, align="center")
            bg.text((960, 740), f"{member.name} is member #{member.guild.member_count}!", color="white", font=font_small, align="center")

            image_bytes = BytesIO()
            bg.image.save(image_bytes, format="PNG")
            image_bytes.seek(0)
            bg_file = discord.File(fp=image_bytes, filename=image_filename)

            await welcome_channel.send(f"Thanks for joining {member.guild.name}, {member.mention}!")
            await welcome_channel.send(file=bg_file)

        except Exception as e:
            print("[ERROR] Exception in welcome cog:", e)

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
