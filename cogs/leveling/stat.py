import discord
from discord.ext import commands
from .database import get_user, get_top_users, make_progress_bar, LEVEL_UP_MULTIPLIER

class LevelStat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="level", description="Check your or another user's level")
    async def level(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = get_user(member.id)
        if user:
            xp, level = user[1], user[2]
            xp_needed = level * LEVEL_UP_MULTIPLIER
            progress = make_progress_bar(xp, xp_needed)

            embed = discord.Embed(
                title=f"{member.name}'s Stats",
                description=f"⭐ Level {level}\n"
                            f"🔹 XP: {xp}/{xp_needed}\n"
                            f"{progress}",
                color=discord.Color.blue(),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{member.mention} hasn’t started gaining XP yet!")

    @discord.app_commands.command(name="leaderboard", description="Show top 10 users by level and XP")
    async def leaderboard(self, interaction: discord.Interaction):
        top_users = get_top_users(10)
        if not top_users:
            return await interaction.response.send_message("⚠ No data available yet.")

        embed = discord.Embed(title=f"🏆 {interaction.guild.name}'s Leaderboard", color=discord.Color.gold())
        rank = 1
        for user_id, xp, level in top_users:
            member = interaction.guild.get_member(user_id)
            name = member.name if member else f"User ID {user_id}"
            xp_needed = level * LEVEL_UP_MULTIPLIER
            progress = make_progress_bar(xp, xp_needed)

            embed.add_field(
                name=f"#{rank} {name}",
                value=f"⭐ Level {level} | {xp}/{xp_needed} XP\n{progress}",
                inline=False,
            )
            rank += 1

        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed)