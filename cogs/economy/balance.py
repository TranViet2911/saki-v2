import discord
from discord.ext import commands
from .database import get_economy_user

class EconomyBalance(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @discord.app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = get_economy_user(member.id)
        wallet, bank = user[1], user[2]

        embed = discord.Embed(
            title=f"<:economy:1413851964864856195> {member.name}'s Balance",
            description=f"<:wallet:1413852815822028830> Wallet: **{wallet}** <:crystal:1413851240412217395>\n"
                        f"<:bank:1413852830229467146> Bank: **{bank}** <:crystal:1413851240412217395>",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)