from discord.ext import commands
from discord import app_commands
import discord
from utils import ui
from typing import Literal

class Leaderboards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(description="Muestra los mejores usuarios en diferentes categorías")
    @app_commands.describe(category="Categoría del ranking (coins/xp/marriage)")
    async def top(self, ctx, category: Literal["coins", "xp", "marriage"] = "coins"):
        """Leaderboard - &top [coins|xp|marriage]"""
        # category ya es verificado por Discord al usar Slash, pero mantenemos lógica simple
        
        if category == "coins":
            await self._show_coins_lb(ctx)
        elif category == "xp":
            await self._show_xp_lb(ctx)
        elif category == "marriage":
            await self._show_marriage_lb(ctx)
        else:
            await ctx.send(embed=ui.error_embed("Categoría inválida: coins, xp, marriage"))
    
    async def _show_coins_lb(self, ctx):
        """Leaderboard de coins"""
        economy = self.bot.get_cog('Economy')
        if not economy:
            await ctx.send(embed=ui.error_embed("Economy cog no encontrado"))
            return
        
        sorted_users = sorted(
            economy.economy.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        embed = ui.simple_embed(
            title="💰 Leaderboard de Coins",
            description="Top 10 usuarios más ricos",
            color=discord.Color.gold()
        )
        
        for i, (user_id, balance) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"#{i}"
                embed.add_field(
                    name=f"{medal} {user.name}",
                    value=f"💰 **{balance}** coins",
                    inline=False
                )
            except:
                pass
        
        await ctx.send(embed=embed)
    
    async def _show_xp_lb(self, ctx):
        """Leaderboard de XP"""
        xp = self.bot.get_cog('XP')
        if not xp:
            await ctx.send(embed=ui.error_embed("XP cog no encontrado"))
            return
        
        sorted_users = sorted(
            xp.xp_data.items(),
            key=lambda x: (x[1]['level'], x[1]['xp']),
            reverse=True
        )[:10]
        
        embed = ui.simple_embed(
            title="⭐ Leaderboard de XP",
            description="Top 10 usuarios más experimentados",
            color=discord.Color.purple()
        )
        
        for i, (user_id, data) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"#{i}"
                embed.add_field(
                    name=f"{medal} {user.name}",
                    value=f"⭐ Nivel {data['level']} ({data['xp']} XP)",
                    inline=False
                )
            except:
                pass
        
        await ctx.send(embed=embed)
    
    async def _show_marriage_lb(self, ctx):
        """Leaderboard de parejas"""
        profile = self.bot.get_cog('Profile')
        if not profile:
            await ctx.send(embed=ui.error_embed("Profile cog no encontrado"))
            return
        
        couples = []
        seen = set()
        
        for user_id, data in profile.profiles.items():
            spouse_id = data.get('married_to')
            if spouse_id and user_id not in seen and spouse_id not in seen:
                couples.append((user_id, spouse_id))
                seen.add(user_id)
                seen.add(spouse_id)
        
        if not couples:
            await ctx.send(embed=ui.info_embed("Parejas", "No hay parejas registradas"))
            return
        
        embed = ui.simple_embed(
            title="💑 Parejas Registradas",
            description=f"Total de parejas: {len(couples)}",
            color=discord.Color.pink()
        )
        
        for i, (user1_id, user2_id) in enumerate(couples[:10], 1):
            try:
                user1 = await self.bot.fetch_user(int(user1_id))
                user2 = await self.bot.fetch_user(int(user2_id))
                embed.add_field(
                    name=f"💒 Pareja #{i}",
                    value=f"{user1.name} ❤️ {user2.name}",
                    inline=False
                )
            except:
                pass
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboards(bot))
