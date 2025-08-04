from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name = 'ping', description = 'Kiểm tra độ trễ của bot tới Discord')
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f'Pong! 🏓 {latency}ms')

		async def cog_load(self):
        await self.bot.tree.sync()

		async def setup(bot):
    		await bot.add_cog(Ping(bot))