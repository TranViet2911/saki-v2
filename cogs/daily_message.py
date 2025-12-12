import discord
from discord.ext import commands, tasks
import datetime
import asyncio


CHANNEL_ID = 1368588307998576711   # <-- put your channel id here


class DailyMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    @tasks.loop(time=datetime.time(hour=0, minute=0, second=0, tzinfo=datetime.timezone(datetime.timedelta(hours=7))))
    async def daily_task(self):
        """Runs automatically every day at 00:00 GMT+7"""
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel is None:
            print("[DailyMessage] ERROR: Channel not found!")
            return

        try:
            await channel.send("https://storage.sekai.best/sekai-jp-assets/music/jacket/jacket_s_128/jacket_s_128.png")
        except Exception as e:
            print("[DailyMessage] Failed to send message:", e)

    @daily_task.before_loop
    async def before_daily_task(self):
        print("[DailyMessage] Waiting for bot to be ready...")
        await self.bot.wait_until_ready()
        print("[DailyMessage] Daily task started")


async def setup(bot):
    await bot.add_cog(DailyMessage(bot))