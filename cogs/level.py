import discord
from discord.ext import commands
import sqlite3

XP_PER_MESSAGE = 10
LEVEL_UP_MULTIPLIER = 100

# ------------------------------
# DATABASE SETUP
# ------------------------------
conn = sqlite3.connect("levels.db")
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


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        level, xp = add_xp(message.author.id, XP_PER_MESSAGE)
        xp_needed = level * LEVEL_UP_MULTIPLIER

        if xp == XP_PER_MESSAGE and level == 1:  # first record
            await message.channel.send(f"🎉 {message.author.mention} started their journey at **Level 1**!")
        elif xp == 0:  # means leveled up
            await message.channel.send(f"🔥 {message.author.mention} leveled up to **Level {level}!**")

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        """Check your level"""
        member = member or ctx.author
        user = get_user(member.id)
        if user:
            xp, level = user[1], user[2]
            xp_needed = level * LEVEL_UP_MULTIPLIER
            await ctx.send(f"📊 {member.mention} is **Level {level}** with **{xp}/{xp_needed} XP**.")
        else:
            await ctx.send(f"{member.mention} hasn’t started gaining XP yet!")


async def setup(bot):
    await bot.add_cog(Leveling(bot))
