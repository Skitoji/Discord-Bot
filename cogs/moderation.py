from discord.ext import commands
import discord
import json
import os
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns_file = "data/warns.json"
        self.load_warns()
    
    def load_warns(self):
        if os.path.exists(self.warns_file):
            with open(self.warns_file) as f:
                self.warns = json.load(f)
        else:
            self.warns = {}
    
    def save_warns(self):
        with open(self.warns_file, "w") as f:
            json.dump(self.warns, f, indent=2)
    
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, user: discord.Member, *, reason="Sin razón"):
        """Advertir usuario - &warn <usuario> [razón]"""
        if user.top_role >= ctx.author.top_role:
            await ctx.send("❌ No puedes advertir a este usuario")
            return
        
        user_id = str(user.id)
        if user_id not in self.warns:
            self.warns[user_id] = []
        
        self.warns[user_id].append({
            'reason': reason,
            'by': ctx.author.name
        })
        
        self.save_warns()
        
        warn_count = len(self.warns[user_id])
        embed = discord.Embed(
            title="⚠️ Usuario Advertido",
            description=f"{user.mention} ha sido advertido\n\n**Razón:** {reason}",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Advertencias: {warn_count}/3")
        
        await ctx.send(embed=embed)
        
        # DM al usuario
        try:
            await user.send(f"⚠️ Has sido advertido en {ctx.guild.name}\n**Razón:** {reason}\n**Advertencias:** {warn_count}/3")
        except:
            pass
        
        # Kick después de 3 warns
        if warn_count >= 3:
            await ctx.send(f"❌ {user.mention} ha sido expulsado por acumular 3 advertencias")
            await user.kick(reason="3 advertencias acumuladas")
            del self.warns[user_id]
            self.save_warns()
    
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, user: discord.Member, duration: int, *, reason="Sin razón"):
        """Silenciar usuario - &mute <usuario> <segundos> [razón]"""
        if user.top_role >= ctx.author.top_role:
            await ctx.send("❌ No puedes silenciar a este usuario")
            return
        
        # Crear rol de muted si no existe
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)
        
        await user.add_roles(muted_role)
        
        embed = discord.Embed(
            title="🔇 Usuario Silenciado",
            description=f"{user.mention} ha sido silenciado\n**Razón:** {reason}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Duración: {duration}s")
        
        await ctx.send(embed=embed)
        
        # Remover rol después del tiempo
        await asyncio.sleep(duration)
        await user.remove_roles(muted_role)
        await ctx.send(f"🔊 {user.mention} ha sido desilenciado")
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason="Sin razón"):
        """Expulsar usuario - &kick <usuario> [razón]"""
        if user.top_role >= ctx.author.top_role:
            await ctx.send("❌ No puedes expulsar a este usuario")
            return
        
        embed = discord.Embed(
            title="👢 Usuario Expulsado",
            description=f"{user.mention} ha sido expulsado\n**Razón:** {reason}",
            color=discord.Color.red()
        )
        
        await ctx.send(embed=embed)
        await user.kick(reason=reason)
        
        try:
            await user.send(f"👢 Has sido expulsado de {ctx.guild.name}\n**Razón:** {reason}")
        except:
            pass
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason="Sin razón"):
        """Banear usuario - &ban <usuario> [razón]"""
        if user.top_role >= ctx.author.top_role:
            await ctx.send("❌ No puedes banear a este usuario")
            return
        
        embed = discord.Embed(
            title="🔨 Usuario Baneado",
            description=f"{user.mention} ha sido baneado\n**Razón:** {reason}",
            color=discord.Color.dark_red()
        )
        
        await ctx.send(embed=embed)
        await ctx.guild.ban(user, reason=reason)
        
        try:
            await user.send(f"🔨 Has sido baneado de {ctx.guild.name}\n**Razón:** {reason}")
        except:
            pass
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="Sin razón"):
        """Desbanear usuario - &unban <id> [razón]"""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"✅ {user.mention} ha sido desbaneado")
        except:
            await ctx.send("❌ Usuario no encontrado")
    
    @commands.command()
    async def warns(self, ctx, user: discord.Member = None):
        """Ver advertencias - &warns [usuario]"""
        if user is None:
            user = ctx.author
        
        user_id = str(user.id)
        warn_list = self.warns.get(user_id, [])
        
        if not warn_list:
            await ctx.send(f"{user.mention} no tiene advertencias")
            return
        
        embed = discord.Embed(
            title=f"⚠️ Advertencias de {user.name}",
            color=discord.Color.orange()
        )
        
        for i, warn in enumerate(warn_list, 1):
            embed.add_field(
                name=f"Advertencia #{i}",
                value=f"**Razón:** {warn['reason']}\n**Por:** {warn['by']}",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
