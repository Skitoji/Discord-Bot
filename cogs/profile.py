from discord.ext import commands
import discord
import json
import os
from utils import ui

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.profile_file = "data/profiles.json"
        self.load_profiles()
    
    def load_profiles(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file) as f:
                self.profiles = json.load(f)
        else:
            self.profiles = {}
    
    def save_profiles(self):
        with open(self.profile_file, "w") as f:
            json.dump(self.profiles, f, indent=2)
    
    def get_profile(self, user_id):
        return self.profiles.get(str(user_id), {
            'bio': 'Sin biografía',
            'married_to': None,
            'badges': []
        })
    
    @commands.hybrid_command(description="Establece tu biografía personal")
    async def bio(self, ctx, *, text: str):
        """Establecer tu biografía - &bio <texto>"""
        if len(text) > 100:
            await ctx.send(embed=ui.error_embed("La biografía no puede exceder 100 caracteres"))
            return
        
        user_id = str(ctx.author.id)
        if user_id not in self.profiles:
            self.profiles[user_id] = {
                'bio': text,
                'married_to': None,
                'badges': []
            }
        else:
            self.profiles[user_id]['bio'] = text
        
        self.save_profiles()
        await ctx.send(embed=ui.success_embed(f"Biografía actualizada: *{text}*"))
    
    @commands.hybrid_command(description="Propón matrimonio a otro usuario")
    async def marry(self, ctx, user: discord.Member):
        """Casarse con otro usuario"""
        if user == ctx.author:
            await ctx.send(embed=ui.error_embed("No puedes casarte contigo mismo"))
            return
        
        author_id = str(ctx.author.id)
        user_id = str(user.id)
        
        if author_id not in self.profiles:
            self.profiles[author_id] = {'bio': 'Sin biografía', 'married_to': None, 'badges': []}
        if user_id not in self.profiles:
            self.profiles[user_id] = {'bio': 'Sin biografía', 'married_to': None, 'badges': []}
        
        if self.profiles[author_id]['married_to']:
            await ctx.send(embed=ui.error_embed("Ya estás casado"))
            return
        
        # Enviar propuesta con botones
        embed = ui.simple_embed(
            "💍 Propuesta de Matrimonio",
            f"{ctx.author.mention} te propone matrimonio",
            color=discord.Color.pink()
        )
        
        view = ui.AcceptDenyView(target_user=user)
        msg = await ctx.send(content=user.mention, embed=embed, view=view)
        
        await view.wait()
        
        if view.value is None:
            await ctx.send(embed=ui.info_embed("⏱️ Expirado", "La propuesta expiró"))
        elif view.value:
            self.profiles[author_id]['married_to'] = user_id
            self.profiles[user_id]['married_to'] = author_id
            self.save_profiles()
            await ctx.send(embed=ui.success_embed(f"💒 ¡{ctx.author.mention} y {user.mention} ahora están casados!"))
        else:
            await ctx.send(embed=ui.error_embed(f"{user.mention} rechazó la propuesta"))
            
        # Desactivar botones después de uso
        for child in view.children:
            child.disabled = True
        await msg.edit(view=view)
    
    @commands.hybrid_command(description="Divórciate de tu pareja actual")
    async def divorce(self, ctx):
        """Divorciarse"""
        user_id = str(ctx.author.id)
        
        if user_id not in self.profiles or not self.profiles[user_id].get('married_to'):
            await ctx.send(embed=ui.error_embed("No estás casado"))
            return
        
        spouse_id = self.profiles[user_id]['married_to']
        self.profiles[user_id]['married_to'] = None
        self.profiles[spouse_id]['married_to'] = None
        self.save_profiles()
        
        await ctx.send(embed=ui.success_embed("💔 Divorcio procesado"))

    @commands.hybrid_command(aliases=['perfil'], description="Ver tu perfil o el de otro usuario")
    async def profile(self, ctx, user: discord.Member = None):
        """Ver perfil con estadísticas"""
        target = user or ctx.author
        
        # Obtener datos de XP
        xp_cog = self.bot.get_cog('XP')
        level = 1
        xp = 0
        xp_next = 100
        if xp_cog:
            data = xp_cog.xp_data.get(str(target.id), {"xp": 0, "level": 1})
            level = data["level"]
            xp = data["xp"]
            xp_next = xp_cog.xp_to_next(level)
            
        # Obtener datos de Economy
        economy_cog = self.bot.get_cog('Economy')
        balance = 0
        if economy_cog:
            balance = economy_cog.get_balance(target.id)
            
        # Datos del perfil local
        profile_data = self.get_profile(target.id)
        bio = profile_data['bio']
        spouse_id = profile_data['married_to']
        spouse_name = "Nadie"
        if spouse_id:
            try:
                spouse = await self.bot.fetch_user(int(spouse_id))
                spouse_name = spouse.name
            except:
                spouse_name = "Desconocido"
        
        # Crear Embed Estilo Nekotina (Simplificado)
        embed = discord.Embed(
            color=discord.Color.magenta()
        )
        
        # Header (Nombre + Badges mockup)
        embed.set_author(name=f"{target.name} (@{target.name})", icon_url=target.display_avatar.url)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # Nivel / XP / Rank
        # Nota: Rank requeriría ordenar toda la DB, para simplificar mostramos Nivel/XP
        embed.add_field(
            name="⭐ Nivel",
            value=f"**{level}** ({xp}/{xp_next} XP)",
            inline=True
        )
        
        embed.add_field(
            name="💰 Coins",
            value=f"{balance}",
            inline=True
        )
        
        # Espacio vacío para balancear si se quiere, o Stats generales
        embed.add_field(name="\u200b", value="\u200b", inline=True)
         
        # Body Stats (Bio, Marry, Registered)
        embed.add_field(
            name="📝 Biografía",
            value=bio,
            inline=False
        )
        
        embed.add_field(
            name="💍 Matrimonio",
            value=f"❤️ {spouse_name}",
            inline=True
        )
        
        # Fecha de registro
        created_at = target.created_at.strftime("%d/%m/%Y")
        embed.set_footer(text=f"Registrado el {created_at}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
