from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, ext):
        try:
            await ctx.bot.reload_extension(f"cogs.{ext}")
            await ctx.send(f"🔄 {ext} recargado")
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(Admin(bot))
