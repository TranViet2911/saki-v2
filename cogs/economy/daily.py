import datetime
from discord.ext import commands
import discord
from .database import set_daily, can_claim_today, update_wallet

class EconomyDaily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[EconomyDaily] Cog loaded ✅")  # Debug print

    ### DAILY COMMAND ###
    @discord.app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        try:
            print(f"[Daily] Command triggered by {interaction.user} ({interaction.user.id})")  # Debug log

            user_id = interaction.user.id
            reward = 300

            now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)  # GMT+7
            today_str = now.strftime("%Y-%m-%d")

            if can_claim_today(user_id):
                print(f"[Daily] {user_id} can claim today ✅")  # Debug

                update_wallet(user_id, reward)
                set_daily(user_id)

                embed = discord.Embed(
                    title="Daily Claim",
                    description=f"You claimed your **{reward}** <:crystal:1413851240412217395>. Please come back tomorrow!",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.set_footer(text="Daily reward is reset at 12AM (GMT+7)")
                await interaction.response.send_message(embed=embed)

            else:
                print(f"[Daily] {user_id} already claimed today ❌")  # Debug

                # find next reset (midnight GMT+7)
                tomorrow = now + datetime.timedelta(days=1)
                reset_time = datetime.datetime.combine(tomorrow.date(), datetime.time.min)  # 00:00
                remaining = reset_time - now

                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)

                time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

                embed = discord.Embed(
                    title="Not so fast!",
                    description=f"You have already claimed your daily reward today.\n"
                                f"You can claim again in **{time_str}** ⏳",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                await interaction.response.send_message(embed=embed)

        except Exception as e:
            # Catch unexpected errors
            print(f"[Daily] ERROR for user {interaction.user.id}: {e}")
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(f"⚠ Error: {e}", ephemeral=True)
                else:
                    await interaction.response.send_message(f"⚠ Error: {e}", ephemeral=True)
            except Exception as inner:
                print(f"[Daily] Failed to send error message: {inner}")