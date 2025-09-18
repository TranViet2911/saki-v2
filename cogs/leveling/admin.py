import discord
from discord.ext import commands
from .database import reset_user, reset_all_users, add_xp, update_wallet, LEVEL_UP_MULTIPLIER, make_progress_bar, set_global_boost, set_role_boost, set_temp_boost, set_user_boost, get_global_boost, get_role_boost, get_temp_boost, get_user_boost

class LevelAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="resetstat", description="Reset a user's stats (Admin only)")
    @commands.has_permissions(administrator=True)
    async def resetstat(self, interaction: discord.Interaction, member: discord.Member):
        reset_user(member.id)
        await interaction.response.send_message(f"♻ {member.mention}'s stats reset to Level 1.")

    @discord.app_commands.command(name="resetall", description="Reset ALL users (Admin only)")
    @commands.has_permissions(administrator=True)
    async def resetall(self, interaction: discord.Interaction):
        reset_all_users()
        await interaction.response.send_message("♻ All users have been reset to Level 1.")

    @discord.app_commands.command(name="editxp", description="Edit a user's XP (Admin only)")
    @commands.has_permissions(administrator=True)
    async def editxp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount == 0:
            return await interaction.response.send_message("⚠ Provide a non-zero XP amount.", ephemeral=True)

        level, xp, leveled_up, old_level = add_xp(member.id, amount)
        msg = f"✅ {member.mention} now has {xp} XP at Level {level}."

        if leveled_up:
            reward = 100
            update_wallet(member.id, reward)

            xp_needed_next = level * LEVEL_UP_MULTIPLIER
            progress = make_progress_bar(xp, xp_needed_next)

            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"{member.mention} leveled up to **{level}**!\n"
                            f"{progress}\n"
                            f"-# *+{reward}* 💎",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(msg, embed=embed)
        else:
            await interaction.response.send_message(msg)

    # Global Boost
    @discord.app_commands.command(name="setxpboost", description="Set a global XP multiplier (Admin only)")
    @commands.has_permissions(administrator=True)
    async def setxpboost(self, interaction: discord.Interaction, multiplier: float):
        new_val = set_global_boost(multiplier)
        await interaction.response.send_message(f"🌍 Global XP boost set to **x{new_val}**")

    @discord.app_commands.command(name="getxpboost", description="Check current global XP multiplier")
    async def getxpboost(self, interaction: discord.Interaction):
        boost = get_global_boost()
        await interaction.response.send_message(f"🌍 Current global XP boost: **x{boost}**")

    # User Boost
    @discord.app_commands.command(name="setuserboost", description="Set a user's XP multiplier (Admin only)")
    @commands.has_permissions(administrator=True)
    async def setuserboost(self, interaction: discord.Interaction, member: discord.Member, multiplier: float):
        set_user_boost(member.id, multiplier)
        await interaction.response.send_message(f"👤 {member.mention}'s XP boost set to **x{multiplier}**")

    @discord.app_commands.command(name="getuserboost", description="Check a user's XP multiplier")
    async def getuserboost(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        boost = get_user_boost(member.id)
        await interaction.response.send_message(f"👤 {member.mention}'s XP boost: **x{boost}**")

    # Role Boost
    @discord.app_commands.command(name="setroleboost", description="Set a role's XP multiplier (Admin only)")
    @commands.has_permissions(administrator=True)
    async def setroleboost(self, interaction: discord.Interaction, role: discord.Role, multiplier: float):
        set_role_boost(role.id, multiplier)
        await interaction.response.send_message(f"📌 Role {role.name} XP boost set to **x{multiplier}**")

    @discord.app_commands.command(name="getroleboost", description="Check a role's XP multiplier")
    async def getroleboost(self, interaction: discord.Interaction, role: discord.Role):
        boost = get_role_boost(role.id)
        await interaction.response.send_message(f"📌 Role {role.name} XP boost: **x{boost}**")

    # Temp Boost
    @discord.app_commands.command(name="settempboost", description="Give a temporary XP boost to a user (Admin only)")
    @commands.has_permissions(administrator=True)
    async def settempboost(self, interaction: discord.Interaction, member: discord.Member, multiplier: float, minutes: int):
        set_temp_boost(member.id, multiplier, minutes)
        await interaction.response.send_message(f"⏳ {member.mention} gets x{multiplier} XP for {minutes} minutes!")

    @discord.app_commands.command(name="gettempboost", description="Check a user's temporary XP boost")
    async def gettempboost(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        boost = get_temp_boost(member.id)
        await interaction.response.send_message(f"⏳ {member.mention}'s temporary XP boost: **x{boost}**")

    # Show all boosts
    @discord.app_commands.command(name="boosts", description="Show all active XP boosts for you or another user")
    async def boosts(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user

        # Collect boosts
        global_boost = get_global_boost()
        user_boost = get_user_boost(member.id)
        role_boosts = [(role.name, get_role_boost(role.id)) for role in member.roles if get_role_boost(role.id) != 1.0]
        temp_boost = get_temp_boost(member.id)

        # Calculate total
        total_mult = global_boost * user_boost * temp_boost
        for _, mult in role_boosts:
            total_mult *= mult

        embed = discord.Embed(
            title=f"⚡ XP Boosts for {member.display_name}",
            color=discord.Color.purple()
        )
        embed.add_field(name="🌍 Global", value=f"x{global_boost}", inline=False)
        embed.add_field(name="👤 User", value=f"x{user_boost}", inline=False)
        embed.add_field(name="⏳ Temporary", value=f"x{temp_boost}", inline=False)

        if role_boosts:
            roles_text = "\n".join([f"{name}: x{mult}" for name, mult in role_boosts])
            embed.add_field(name="📌 Roles", value=roles_text, inline=False)
        else:
            embed.add_field(name="📌 Roles", value="None", inline=False)

        embed.add_field(name="🔮 Final Multiplier", value=f"**x{total_mult:.2f}**", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)