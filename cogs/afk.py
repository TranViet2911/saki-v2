import discord

from discord.ext import commands

class AFK(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.afk_users = {}  # {user_id: reason}

    # Slash command

    @discord.app_commands.command(name="afk", description="Set your AFK status")

    async def afk(self, interaction: discord.Interaction, reason: str = "AFK"):

        self.afk_users[interaction.user.id] = reason

        await interaction.response.send_message(

            f"<a:afk:1402606586270322800> {interaction.user.mention} is now AFK: {reason}", ephemeral=False

        )

    # Check tin nhắn để xóa afk

    @commands.Cog.listener()

    async def on_message(self, message):

        if message.author.bot:

            return

        # xóa afk khi kiểm tra đc tin nhắn gửi đi

        if message.author.id in self.afk_users:

            del self.afk_users[message.author.id]

            await message.channel.send(

                f"<a:afk:1402606586270322800> Welcome back, {message.author.mention}! You are no longer AFK."

            )

        # Tbao nếu bất cứ ng nào ping afk

        for user in message.mentions:

            if user.id in self.afk_users:

                reason = self.afk_users[user.id]

                await message.channel.send(

                    f"<a:afk:1402606586270322800> {user.display_name} is AFK: {reason}"

                )

        await self.bot.process_commands(message)

    async def cog_load(self):


        pass self.bot.tree.add_command(self.afk);

async def setup(bot):
    await bot.add_cog(AFK(bot))