import discord
from discord.ext import commands
import sqlite3
import random

XP_MIN = 10
XP_MAX = 20
LEVEL_UP_MULTIPLIER = 100

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

def get_user(user_id):
    c.execute("SELECT * FROM levels WHERE user_id = ?", (user_id,))
    return c.fetchone()

def add_xp(user_id, xp):
    user = get_user(user_id)
    if user is None:
        c.execute("INSERT INTO levels (user_id, xp, level) VALUES (?, ?, ?)", (user_id, xp, 1))
        conn.commit()
        return 1, xp
    else:
        current_xp, current_level = user[1], user[2]
        new_xp = current_xp + xp
        xp_needed = current_level * LEVEL_UP_MULTIPLIER

        if new_xp >= xp_needed:
            new_level = current_level + 1
            new_xp = new_xp - xp_needed
            c.execute("UPDATE levels SET xp = ?, level = ? WHERE user_id = ?", (new_xp, new_level, user_id))
            conn.commit()
            return new_level, new_xp
        else:
            c.execute("UPDATE levels SET xp = ? WHERE user_id = ?", (new_xp, user_id))
            conn.commit()
            return current_level, new_xp

def reset_user(user_id):
    c.execute("UPDATE levels SET xp = 0, level = 1 WHERE user_id = ?", (user_id,))
    conn.commit()

def get_top_users(limit=10):
    c.execute("SELECT * FROM levels ORDER BY level DESC, xp DESC LIMIT ?", (limit,))
    return c.fetchall()

# ------------------------------
# PROGRESS BAR
# ------------------------------
def make_progress_bar(xp, xp_needed, length=10):
    progress = int((xp / xp_needed) * length) if xp_needed > 0 else 0
    bar = "▓" * progress + "░" * (length - progress)
    percent = int((xp / xp_needed) * 100) if xp_needed > 0 else 0
    return f"{bar} {percent}%"


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------
    # XP Gain Listener
    # ------------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        gained_xp = random.randint(XP_MIN, XP_MAX)  # 🎲 Random XP per message
        level, xp = add_xp(message.author.id, gained_xp)

        # 🎉 First record
        if xp == gained_xp and level == 1:
            await message.channel.send(f"🎉 {message.author.mention} started their journey at **Level 1**!")

        # 🔥 Level up
        elif xp == 0:
            c.execute("SELECT user_id FROM levels ORDER BY level DESC, xp DESC")
            all_users = [row[0] for row in c.fetchall()]
            rank = all_users.index(message.author.id) + 1

            xp_needed = level * LEVEL_UP_MULTIPLIER
            progress = make_progress_bar(xp, xp_needed)

            embed = discord.Embed(
                title="<:lightpinkflower:1406242431640277002> Level Up!",
                description=(
                    f"{message.author.mention} leveled up to **Level {level}!**\n"
                    f"<a:trophy:1406253183227138078> Rank: {rank}\n"
                    f"<:xp:1406259092309282978> {xp}/{xp_needed}\n"
                    f"{progress}"
                ),
                colour=0x00b0f4
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text="Saki 2.0 / Made by Groovy")

            await message.channel.send(embed=embed)

    # ------------------------------
    # Slash Commands
    # ------------------------------
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

            embed = discord.Embed(
                title=f"📊 {member.name}'s Level",
                description=(
                    f"{member.mention} is **Level {level}**\n"
                    f"<:xp:1406259092309282978> {xp}/{xp_needed}\n"
                    f"{progress}"
                ),
                color=0x00b0f4
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Saki 2.0 / Made by Groovy")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{member.mention} hasn’t started gaining XP yet!")

    @discord.app_commands.command(name="resetstat", description="Reset a user's stats (Admin only)")
    @commands.has_permissions(administrator=True)
    async def resetstat(self, interaction: discord.Interaction, member: discord.Member):
        reset_user(member.id)
        await interaction.response.send_message(f"♻ {member.mention}'s stats have been reset to **Level 1** with **0 XP**.")

    @discord.app_commands.command(name="leaderboard", description="Show top 10 users by level and XP")
    async def leaderboard(self, interaction: discord.Interaction):
        top_users = get_top_users(10)
        if not top_users:
            return await interaction.response.send_message("⚠ No data available yet.")

        embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())
        rank = 1
        for user_id, xp, level in top_users:
            member = interaction.guild.get_member(user_id)
            name = member.name if member else f"User ID {user_id}"
            xp_needed = level * LEVEL_UP_MULTIPLIER
            progress = make_progress_bar(xp, xp_needed)

            embed.add_field(
                name=f"#{rank} {name}",
                value=f"⭐ Level {level} | <:xp:1406259092309282978> {xp}/{xp_needed}\n{progress}",
                inline=False
            )
            rank += 1

        embed.set_footer(text="Saki 2.0 / Made by Groovy")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Leveling(bot))
