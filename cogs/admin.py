from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, ext):
        try:
            await ctx.bot.reload_extension(f"cogs.{ext}")
            await ctx.send(f"🔄 {ext} recargado")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, ext):
        try:
            await ctx.bot.load_extension(f"cogs.{ext}")
            await ctx.send(f"✅ {ext} cargado")
        except Exception as e:
            await ctx.send(f"Error: {e}")
            
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx, spec: str = None):
        """
        Sincronizar comandos slash
        Uso: 
        &sync -> Sincroniza globalmente (lento)
        &sync . -> Sincroniza solo en el servidor actual (rápido)
        """
        if spec == ".":
            # Sincronizar solo en este guild (instantáneo)
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"✅ **{len(synced)}** comandos sincronizados en este servidor. ¡Deberían aparecer ya!")
        else:
            # Sincronizar globalmente (puede tardar 1 hora)
            await ctx.send("⏳ Sincronizando globalmente... (esto puede tardar hasta 1 hora en actualizarse en Discord)")
            synced = await ctx.bot.tree.sync()
            await ctx.send(f"✅ **{len(synced)}** comandos sincronizados globalmente.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
