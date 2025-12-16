import discord
from discord.ext import commands
import json, os

def cargar_contador():
    if os.path.exists("data/contador.txt"):
        try:
            content = open("data/contador.txt").read().strip()
            return int(content) if content else 0
        except:
            return 0
    return 0

def guardar_contador(num):
    open("data/contador.txt","w").write(str(num))

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.contador = cargar_contador()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Cargar config dinámica
        config = {}
        if os.path.exists("data/welcome_config.json"):
            with open("data/welcome_config.json") as f:
                config = json.load(f)
        
        channel_id = config.get("channel_id")
        banner = config.get("welcome_image")
        
        if not channel_id:
            return

        self.contador += 1
        guardar_contador(self.contador)

        # Config Values
        title = config.get("welcome_title", "Bienvenid@!")
        desc = config.get("welcome_description", "{mention} ha entrado").replace("{mention}", member.mention).replace("{count}", str(self.contador)).replace("{server}", member.guild.name)
        footer = config.get("footer_text", "").replace("{count}", str(self.contador))

        # Mensaje DM (Limpio)
        try:
            await member.send(f"{desc}\n\nEres el usuario n° **{self.contador}**")
        except: pass

        canal = member.guild.get_channel(int(channel_id))

        if canal:
            embed = discord.Embed(
                title=title,
                description=desc,
                color=discord.Color.from_rgb(255,20,90)
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            if banner:
                embed.set_image(url=banner)
            if footer:
                embed.set_footer(text=footer)

            await canal.send(embed=embed)

    async def emit_test_welcome(self, member):
        """Simular una bienvenida para testing"""
        await self.on_member_join(member)

    @commands.hybrid_command(description="Prueba el mensaje de bienvenida")
    @commands.has_permissions(administrator=True)
    async def testwelcome(self, ctx):
        """Envía un mensaje de bienvenida de prueba"""
        await ctx.send("🔄 Generando bienvenida de prueba...", ephemeral=True)
        await self.emit_test_welcome(ctx.author)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
