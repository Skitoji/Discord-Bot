import discord
from discord.ext import commands
from utils.colors import COLORS

class AutoRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def crear_colores(self, ctx):
        await ctx.send("🎨 Creando roles de colores...")

        for name, color in COLORS.items():
            if discord.utils.get(ctx.guild.roles, name=name):
                continue
            try:
                await ctx.guild.create_role(name=name, colour=color)
            except discord.Forbidden:
                await ctx.send("❌ No tengo permisos para crear roles")
                return
            except Exception as e:
                await ctx.send(f"❌ Error: {e}")
                return

        await ctx.send("✅ Roles de colores creados exitosamente.")

    @commands.command()
    async def colores(self, ctx):
        embed = discord.Embed(
            title="🎨 Elige tu color",
            description="Reacciona al color que quieras obtener",
            color=discord.Color.random()
        )

        msg = await ctx.send(embed=embed)
        for emoji in ["🟢","🟡","🔵","🟠","🔴","🟣"]:
            await msg.add_reaction(emoji)

async def setup(bot):
    await bot.add_cog(AutoRoles(bot))
