from discord.ext import commands

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! 🏓 {latency}ms')

async def setup(bot):
    bot.add_cog(Ping(bot))