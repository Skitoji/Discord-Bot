from discord.ext import commands
import discord
import json
import os

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
    
    @commands.command()
    async def bio(self, ctx, *, text):
        """Establecer tu biografía - &bio <texto>"""
        if len(text) > 100:
            await ctx.send("❌ La biografía no puede exceder 100 caracteres")
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
        await ctx.send(f"✅ Biografía actualizada: *{text}*")
    
    @commands.command()
    async def marry(self, ctx, user: discord.Member):
        """Casarse con otro usuario"""
        if user == ctx.author:
            await ctx.send("❌ No puedes casarte contigo mismo")
            return
        
        author_id = str(ctx.author.id)
        user_id = str(user.id)
        
        if author_id not in self.profiles:
            self.profiles[author_id] = {'bio': 'Sin biografía', 'married_to': None, 'badges': []}
        if user_id not in self.profiles:
            self.profiles[user_id] = {'bio': 'Sin biografía', 'married_to': None, 'badges': []}
        
        if self.profiles[author_id]['married_to']:
            await ctx.send("❌ Ya estás casado")
            return
        
        # Enviar propuesta
        embed = discord.Embed(
            title="💍 Propuesta de Matrimonio",
            description=f"{ctx.author.mention} te propone matrimonio\n\nReacciona con ✅ para aceptar",
            color=discord.Color.pink()
        )
        
        msg = await ctx.send(embed=embed, content=user.mention)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        
        def check(reaction, react_user):
            return react_user == user and reaction.message == msg
        
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=60)
            
            if str(reaction.emoji) == '✅':
                self.profiles[author_id]['married_to'] = user_id
                self.profiles[user_id]['married_to'] = author_id
                self.save_profiles()
                await ctx.send(f"💒 ¡{ctx.author.mention} y {user.mention} ahora están casados!")
            else:
                await ctx.send(f"❌ {user.mention} rechazó la propuesta")
        except:
            await ctx.send("⏱️ La propuesta expiró")
    
    @commands.command()
    async def divorce(self, ctx):
        """Divorciarse"""
        user_id = str(ctx.author.id)
        
        if user_id not in self.profiles or not self.profiles[user_id].get('married_to'):
            await ctx.send("❌ No estás casado")
            return
        
        spouse_id = self.profiles[user_id]['married_to']
        self.profiles[user_id]['married_to'] = None
        self.profiles[spouse_id]['married_to'] = None
        self.save_profiles()
        
        await ctx.send("💔 Divorcio procesado")
    
    @commands.command()
    async def perfil(self, ctx, user: discord.Member = None):
        """Ver perfil de usuario"""
        if user is None:
            user = ctx.author
        
        profile = self.get_profile(user.id)
        xp_cog = self.bot.get_cog('XP')
        economy_cog = self.bot.get_cog('Economy')
        
        # Obtener datos
        level = 0
        xp = 0
        if xp_cog:
            xp_data = xp_cog.get_user_xp(user.id)
            level = xp_data['level']
            xp = xp_data['xp']
        
        balance = 0
        if economy_cog:
            balance = economy_cog.get_balance(user.id)
        
        spouse = "Soltero/a"
        if profile.get('married_to'):
            try:
                spouse_user = await self.bot.fetch_user(int(profile['married_to']))
                spouse = spouse_user.name
            except:
                spouse = "Desconocido"
        
        embed = discord.Embed(
            title=f"👤 Perfil de {user.name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar)
        embed.add_field(name="💰 Coins", value=f"{balance}", inline=True)
        embed.add_field(name="⭐ Nivel", value=f"{level}", inline=True)
        embed.add_field(name="📊 XP", value=f"{xp}", inline=True)
        embed.add_field(name="💍 Pareja", value=spouse, inline=True)
        embed.add_field(name="📝 Bio", value=profile.get('bio', 'Sin biografía'), inline=False)
        
        if profile.get('badges'):
            embed.add_field(name="🏆 Badges", value=" ".join(profile['badges']), inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
