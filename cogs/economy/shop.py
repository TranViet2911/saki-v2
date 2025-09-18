import discord
from discord.ext import commands
import json
from .database import load_shop

class EconomyShopList(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        
### SHOP ###
    @discord.app_commands.command(name="shop", description="Browse the shop for some stuff")
    async def shop(self, interaction: discord.Interaction):
        try:
            items = load_shop()
        except FileNotFoundError:
            await interaction.response.send_message(
                "⚠️ `shop.json` not found! Please put it in the same folder as your bot.",
                ephemeral=True
            )
            return
        except Exception as e:
            await interaction.response.send_message(
                f"⚠️ Failed to load shop: `{e}`",
                ephemeral=True
            )
            return

        if not items:
            await interaction.response.send_message("⚠️ The shop is empty!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🍉 Shop",
            description="Here are the items you can buy:",
            color=discord.Color.blue()
        )

        for item in items:
            embed.add_field(
                name=f"{item['id']}. {item['name']} — {item['price']} <:crystal:1413851240412217395>",
                value=item['description'],
                inline=False
            )

        await interaction.response.send_message(embed=embed)
