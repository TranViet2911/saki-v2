import discord
from discord.ext import commands

class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)  # latency in ms
        await ctx.send(f'Pong! 🏓 {latency}ms')

def setup(bot):
    bot.add_cog(ping(bot))