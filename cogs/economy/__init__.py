from .daily import EconomyDaily
from .balance import EconomyBalance
from .shop import EconomyShopList

async def setup(bot):
    await bot.add_cog(EconomyDaily(bot))
    await bot.add_cog(EconomyBalance(bot))
    await bot.add_cog(EconomyShopList(bot))