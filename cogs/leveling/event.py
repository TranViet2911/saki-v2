import discord
from discord.ext import commands
import random
from .database import XP_MIN, XP_MAX, add_xp, make_progress_bar, update_wallet, LEVEL_UP_MULTIPLIER, get_top_users


class LevelEvent(commands.Cogs):
    def __init__(self, bot):
        self.bot = bot
# Event
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        gained_xp = random.randint(XP_MIN, XP_MAX)
        level, xp, leveled_up, old_level = add_xp(message.author.id, gained_xp)

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