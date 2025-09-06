import discord
from discord.ext import commands
import sqlite3
import random
import datetime

conn = sqlite3.connect("s2430_Saki.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER PRIMARY KEY,
                wallet INTEGER,
                bank INTEGER,
                last_daily TEXT
            )""")
conn.commit()

def get_economy_user(user_id):
    c.execute("SELECT * FROM economy WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if user is None:
        c.execute("INSERT INTO economy (user_id, wallet, bank, last_daily) VALUES (?, ?, ?, ?)", (user_id, 0, 0, None))
        conn.commit()
        return (user_id, 0, 0, None)
    return user

def update_wallet(user_id, amount):
    user = get_economy_user(user_id)
    new_wallet = user[1] + amount
    c.execute("UPDATE economy SET wallet = ? WHERE user_id = ?", (new_wallet, user_id))
    conn.commit()

def update_bank(user_id, amount):
    user = get_economy_user(user_id)
    new_bank = user[2] + amount
    c.execute("UPDATE economy SET bank = ? WHERE user_id = ?", (new_bank, user_id))
    conn.commit()

def set_daily(user_id):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    today = now.strftime("%Y-%m-%d")
    c.execute("UPDATE economy SET last_daily = ? WHERE user_id = ?", (today, user_id))
    conn.commit()

def can_claim_today(user_id):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)  # GMT+7
    today = now.strftime("%Y-%m-%d")

    c.execute("SELECT last_daily FROM economy WHERE user_id = ?", (user_id,))
    result = c.fetchone()

    if result is None or result[0] is None:  # never claimed
        return True
    return result[0] != today


### BALANCE COMMAND ###
class Economy(commands.Cog):
    def __init__(self, bot):
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

    ### DAILY COMMAND ###
    @discord.app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        reward = 300

        if can_claim_today(user_id):
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
            embed = discord.Embed(
                title="Not so fast!",
                description="You have already claimed your daily reward today. Please come back tomorrow!",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.set_footer(text="Daily reward is reset at 12AM (GMT+7)")
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))