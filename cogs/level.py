import discord
from discord.ext import commands
import sqlite3
import random
import io
from PIL import Image, ImageDraw, ImageFont

XP_MIN = 10
XP_MAX = 20
LEVEL_UP_MULTIPLIER = 250

# ------------------------------
# DATABASE SETUP
# ------------------------------
conn = sqlite3.connect("s2430_Saki.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS levels (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER,
                level INTEGER
            )""")
conn.commit()


def get_user(user_id: int):
    c.execute("SELECT * FROM levels WHERE user_id = ?", (user_id,))
    return c.fetchone()

def get_economy_user(user_id: int):
    c.execute("SELECT * FROM economy WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if user is None:
        c.execute("INSERT INTO economy (user_id, wallet, bank, last_daily) VALUES (?, ?, ?, ?)",
                  (user_id, 0, 0, None))
        conn.commit()
        return (user_id, 0, 0, None)
    return user

def add_xp(user_id: int, xp_gain: int):
    user = get_user(user_id)
    if user is None:
        c.execute("INSERT INTO levels (user_id, xp, level) VALUES (?, ?, ?)", (user_id, xp_gain, 1))
        conn.commit()
        return 1, xp_gain, False, 0

    current_xp, current_level = user[1], user[2]
    new_xp = current_xp + xp_gain
    new_level = current_level
    leveled_up = False

    xp_needed = new_level * LEVEL_UP_MULTIPLIER
    while new_xp >= xp_needed:
        new_xp -= xp_needed
        new_level += 1
        leveled_up = True
        xp_needed = new_level * LEVEL_UP_MULTIPLIER

    if new_xp < 0:
        new_xp = 0

    c.execute("UPDATE levels SET xp = ?, level = ? WHERE user_id = ?", (new_xp, new_level, user_id))
    conn.commit()
    return new_level, new_xp, leveled_up, current_level


def reset_user(user_id: int):
    c.execute("UPDATE levels SET xp = 0, level = 1 WHERE user_id = ?", (user_id,))
    conn.commit()


def reset_all_users():
    c.execute("UPDATE levels SET xp = 1, level = 1")
    conn.commit()


def get_top_users(limit=10):
    c.execute("SELECT * FROM levels ORDER BY level DESC, xp DESC LIMIT ?", (limit,))
    return c.fetchall()


def update_wallet(user_id: int, amount: int):
    try:
        user = get_economy_user(user_id)  # provided by your economy module
        if user is None:
            c.execute("INSERT OR IGNORE INTO economy (user_id, wallet, bank, last_daily) VALUES (?, ?, ?, ?)",
                      (user_id, 0, 0, None))
            conn.commit()
            user = (user_id, 0, 0, None)

        new_wallet = user[1] + amount
        c.execute("UPDATE economy SET wallet = ? WHERE user_id = ?", (new_wallet, user_id))
        conn.commit()
    except Exception as e:
        print(f"[Economy] Skipped wallet update for {user_id}: {e}")


def make_progress_bar(xp, xp_needed, length=10):
    progress = int((xp / xp_needed) * length) if xp_needed > 0 else 0
    bar = "▓" * progress + "░" * (length - progress)
    percent = int((xp / xp_needed) * 100) if xp_needed > 0 else 0
    return f"{bar} {percent}%"


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        gained_xp = random.randint(XP_MIN, XP_MAX)
        level, xp, leveled_up, old_level = add_xp(message.author.id, gained_xp)

        if old_level == 0 and level == 1 and xp == gained_xp:
            await message.channel.send(
                f"🎉 {message.author.mention} started their journey at **Level 1**!\n"
                f"⚠️ Currently in BETA so data reset may happen sometimes, sorry!"
            )
            return

        if leveled_up:
            c.execute("SELECT user_id FROM levels ORDER BY level DESC, xp DESC")
            all_users = [row[0] for row in c.fetchall()]
            rank = all_users.index(message.author.id) + 1 if message.author.id in all_users else "N/A"

            xp_needed_next = level * LEVEL_UP_MULTIPLIER
            progress = make_progress_bar(xp, xp_needed_next)

            reward = 100
            update_wallet(message.author.id, reward)

            embed = discord.Embed(
                title="<:lightpinkflower:1406242431640277002> Level Up!",
                description=(
                    f"{message.author.mention} leveled up to **Level {level}!**\n"
                    f"<a:trophy:1406253183227138078> Rank: {rank}\n"
                    f"{progress}\n"
                    f"-# *+{reward}* <:crystal:1413851240412217395>"
                ),
                colour=0x00b0f4,
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text="Saki 2.0 | Made by Groovy")
            await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            synced = await self.bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"⚠ Failed to sync commands: {e}")

    @discord.app_commands.command(name="level", description="Check your or another user's level")
    async def level(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = get_user(member.id)
        if user:
            xp, level = user[1], user[2]
            xp_needed = level * LEVEL_UP_MULTIPLIER
            progress = make_progress_bar(xp, xp_needed)

            c.execute("SELECT user_id FROM levels ORDER BY level DESC, xp DESC")
            all_users = [row[0] for row in c.fetchall()]
            rank = all_users.index(member.id) + 1 if member.id in all_users else "N/A"

            embed = discord.Embed(
                title=f"<:lightpinkflower:1406242431640277002> {member.name}'s Stats",
                description=(
                    f"{member.mention} is **Level {level}**\n"
                    f"<a:trophy:1406253183227138078> Rank: {rank}\n"
                    f"<:xp:1406259092309282978> {xp}/{xp_needed}\n"
                    f"{progress}"
                ),
                color=0x00b0f4,
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Saki 2.0 | Made by Groovy")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{member.mention} hasn’t started gaining XP yet!")

    @discord.app_commands.command(name="resetstat", description="Reset a user's stats (Admin only)")
    @commands.has_permissions(administrator=True)
    async def resetstat(self, interaction: discord.Interaction, member: discord.Member):
        reset_user(member.id)
        await interaction.response.send_message(
            f"♻ {member.mention}'s stats have been reset to **Level 1** with **0 XP**."
        )

    @discord.app_commands.command(name="resetall", description="Reset ALL users to Level 1 and 1 XP (Admin only)")
    @commands.has_permissions(administrator=True)
    async def resetall(self, interaction: discord.Interaction):
        reset_all_users()
        await interaction.response.send_message("♻ All users have been reset to **Level 1** with **1 XP**.")

    @discord.app_commands.command(name="leaderboard", description="Show top 10 users by level and XP")
    async def leaderboard(self, interaction: discord.Interaction):
        top_users = get_top_users(10)
        if not top_users:
            return await interaction.response.send_message("⚠ No data available yet.")

        embed = discord.Embed(
            title=f"🏆 {interaction.guild.name}'s Leaderboard",
            color=discord.Color.gold(),
        )
        rank = 1
        for user_id, xp, level in top_users:
            member = interaction.guild.get_member(user_id)
            name = member.name if member else f"User ID {user_id}"
            xp_needed = level * LEVEL_UP_MULTIPLIER
            progress = make_progress_bar(xp, xp_needed)

            embed.add_field(
                name=f"#{rank} {name}",
                value=f"⭐ Level {level} | <:xp:1406259092309282978> {xp}/{xp_needed}\n{progress}",
                inline=False,
            )
            rank += 1

        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text="Saki 2.0 | Made by Groovy")
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="rank", description="Show your rank card")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = get_user(member.id)

        if not user:
            return await interaction.response.send_message(f"{member.mention} hasn’t started gaining XP yet!")

        xp, level = user[1], user[2]
        xp_needed = level * LEVEL_UP_MULTIPLIER

        c.execute("SELECT user_id FROM levels ORDER BY level DESC, xp DESC")
        all_users = [row[0] for row in c.fetchall()]
        rank = all_users.index(member.id) + 1 if member.id in all_users else "N/A"
        total_users = len(all_users)

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
        draw.text((180, 105), f"Rank: #{rank}/{total_users}", font=font_small, fill=(173, 216, 230))

        bar_x, bar_y, bar_width, bar_height = 180, 140, 370, 30
        progress = int((xp / xp_needed) * bar_width) if xp_needed > 0 else 0
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(50, 50, 50))
        draw.rectangle([bar_x, bar_y, bar_x + progress, bar_y + bar_height], fill=(0, 176, 244))
        draw.text((bar_x, bar_y - 25), f"XP: {xp}/{xp_needed}", font=font_small, fill=(200, 200, 200))

        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        buffer.seek(0)

        file = discord.File(buffer, filename="rank.png")
        await interaction.response.send_message(file=file)

    @discord.app_commands.command(name="editxp", description="Edit a user's XP (Admin only)")
    @commands.has_permissions(administrator=True)
    async def editxp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount == 0:
            return await interaction.response.send_message("⚠ Please provide a non-zero amount of XP.", ephemeral=True)

        level, xp, leveled_up, old_level = add_xp(member.id, amount)
        msg = f"✅ Gave **{amount} XP** to {member.mention}. They now have **{xp} XP** at **Level {level}**."

        if leveled_up:
            c.execute("SELECT user_id FROM levels ORDER BY level DESC, xp DESC")
            all_users = [row[0] for row in c.fetchall()]
            rank = all_users.index(member.id) + 1 if member.id in all_users else "N/A"

            xp_needed_next = level * LEVEL_UP_MULTIPLIER
            progress = make_progress_bar(xp, xp_needed_next)

            reward = 100
            update_wallet(member.id, reward)

            embed = discord.Embed(
                title="<:lightpinkflower:1406242431640277002> Level Up!",
                description=(
                    f"{member.mention} leveled up to **Level {level}!**\n"
                    f"<a:trophy:1406253183227138078> Rank: {rank}\n"
                    f"{progress}\n"
                    f"-# *+{reward}* <:crystal:1413851240412217395>"
                ),
                colour=0x00b0f4,
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Saki 2.0 | Made by Groovy")
            await interaction.response.send_message(msg, embed=embed)
        else:
            await interaction.response.send_message(msg)


async def setup(bot):
    await bot.add_cog(Leveling(bot))