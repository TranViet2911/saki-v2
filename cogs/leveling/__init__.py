from .event import LevelEvent
from .stat import LevelStat
from .admin import LevelAdmin
from .rankcard import LevelRankCard

async def setup(bot):
    await bot.add_cog(LevelEvent(bot))
    await bot.add_cog(LevelStat(bot))
    await bot.add_cog(LevelAdmin(bot))
    await bot.add_cog(LevelRankCard(bot))