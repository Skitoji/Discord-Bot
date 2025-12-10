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
        channel_id = self.bot.config.get("WELCOME_CHANNEL_ID")
        role_id = self.bot.config.get("AUTO_ROLE_ID")
        banner = self.bot.config.get("BANNER_URL")
        
        # Validar que los IDs sean válidos
        if not channel_id or not str(channel_id).isdigit():
            return
        if not role_id or not str(role_id).isdigit():
            return

        self.contador += 1
        guardar_contador(self.contador)

        rol = member.guild.get_role(int(role_id))
        if rol: await member.add_roles(rol)

        try:
            await member.send(
                f"😈 Hola {member.name}, bienvenida criatura deliciosa...\n"
                f"🍑 Eres el culito n° **{self.contador}** de Mariana."
            )
        except: pass

        canal = member.guild.get_channel(int(channel_id))

        if canal:
            embed = discord.Embed(
                title="💋 Nuevo CULITO ha llegado 💋",
                description=(
                    f"{member.mention} entró directo al *territorio prohibido de Mariana* 😏\n"
                    f"🍑 Culito número: **{self.contador}**"
                ),
                color=discord.Color.from_rgb(255,20,90)
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_image(url=banner)
            embed.set_footer(text="Mariana observa... 👀")

            await canal.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
