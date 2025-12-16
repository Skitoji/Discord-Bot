from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(description="Muestra todos los comandos disponibles")
    async def comandos(self, ctx):
        """Ver todos los comandos disponibles"""
        from utils import ui
        
        embeds = [
            # Página 1: Música
            self._music_help(),
            # Página 2: Economía
            self._economy_help(),
            # Página 3: Diversión
            self._fun_help(),
            # Página 4: Perfil
            self._profile_help(),
            # Página 5: Leaderboards
            self._leaderboards_help(),
            # Página 6: Moderación
            self._moderation_help(),
            # Página 7: Admin
            self._admin_help(),
        ]
        
        view = ui.PaginatorView(embeds)
        await ctx.send(embed=embeds[0], view=view)
    
    def _music_help(self):
        embed = discord.Embed(
            title="🎵 COMANDOS DE MÚSICA",
            color=discord.Color.blue(),
            description="Reproduce música desde YouTube, Spotify y Apple Music"
        )
        embed.add_field(
            name="&play <canción>",
            value="Reproduce una canción desde YouTube",
            inline=False
        )
        embed.add_field(
            name="&pause",
            value="Pausa la canción actual",
            inline=False
        )
        embed.add_field(
            name="&resume",
            value="Reanuda la canción pausada",
            inline=False
        )
        embed.add_field(
            name="&skip",
            value="Salta a la siguiente canción",
            inline=False
        )
        embed.add_field(
            name="&stop",
            value="Detiene la reproducción",
            inline=False
        )
        embed.add_field(
            name="&queue",
            value="Muestra la cola de canciones",
            inline=False
        )
        embed.add_field(
            name="&nowplaying",
            value="Muestra la canción actual",
            inline=False
        )
        embed.add_field(
            name="&loop",
            value="Activa/desactiva el loop",
            inline=False
        )
        embed.add_field(
            name="&disconnect",
            value="Desconecta el bot del canal de voz",
            inline=False
        )
        return embed
    
    def _economy_help(self):
        embed = discord.Embed(
            title="💰 COMANDOS DE ECONOMÍA",
            color=discord.Color.gold(),
            description="Gana, gasta y gestiona tus coins"
        )
        embed.add_field(
            name="&balance [usuario]",
            value="Ve tu balance de coins o el de otro usuario",
            inline=False
        )
        embed.add_field(
            name="&daily",
            value="Recibe 500 coins cada 24 horas",
            inline=False
        )
        embed.add_field(
            name="&weekly",
            value="Recibe 2000 coins cada 7 días",
            inline=False
        )
        embed.add_field(
            name="&work",
            value="Trabaja y gana 50-200 coins (sin cooldown)",
            inline=False
        )
        embed.add_field(
            name="&gamble <monto>",
            value="Apuesta coins (50% ganar, 50% perder)",
            inline=False
        )
        embed.add_field(
            name="&slots <monto>",
            value="Juega máquina tragamonedas (hasta 5x)",
            inline=False
        )
        embed.add_field(
            name="&pagar <usuario> <monto>",
            value="Transfiere coins a otro usuario",
            inline=False
        )
        embed.add_field(
            name="&leaderboard",
            value="Ve el ranking de usuarios más ricos",
            inline=False
        )
        return embed
    
    def _fun_help(self):
        embed = discord.Embed(
            title="🎮 COMANDOS DE DIVERSIÓN",
            color=discord.Color.purple(),
            description="Juega y diviértete"
        )
        embed.add_field(
            name="&eightball <pregunta>",
            value="La bola mágica responde tu pregunta",
            inline=False
        )
        embed.add_field(
            name="&roulette",
            value="Juega ruleta rusa (50% de ganar dinero)",
            inline=False
        )
        embed.add_field(
            name="&trivia",
            value="Responde una pregunta de trivia",
            inline=False
        )
        embed.add_field(
            name="&meme",
            value="Obtén un meme aleatorio de Reddit",
            inline=False
        )
        embed.add_field(
            name="&flip",
            value="Lanza una moneda (Cara/Cruz)",
            inline=False
        )
        embed.add_field(
            name="&roll [caras]",
            value="Lanza un dado (por defecto 6 caras)",
            inline=False
        )
        embed.add_field(
            name="&choose opción1 | opción2 | opción3",
            value="Elige entre las opciones que das",
            inline=False
        )
        return embed
    
    def _profile_help(self):
        embed = discord.Embed(
            title="👤 COMANDOS DE PERFIL",
            color=discord.Color.pink(),
            description="Personaliza tu perfil"
        )
        embed.add_field(
            name="&bio <texto>",
            value="Establece tu biografía (máx 100 caracteres)",
            inline=False
        )
        embed.add_field(
            name="&marry <usuario>",
            value="Propón matrimonio a otro usuario",
            inline=False
        )
        embed.add_field(
            name="&divorce",
            value="Divórciate de tu pareja",
            inline=False
        )
        embed.add_field(
            name="&perfil [usuario]",
            value="Ve tu perfil o el de otro usuario con stats",
            inline=False
        )
        return embed
    
    def _leaderboards_help(self):
        embed = discord.Embed(
            title="🏆 COMANDOS DE LEADERBOARDS",
            color=discord.Color.orange(),
            description="Ve los rankings"
        )
        embed.add_field(
            name="&top coins",
            value="Top 10 usuarios más ricos",
            inline=False
        )
        embed.add_field(
            name="&top xp",
            value="Top 10 usuarios por experiencia",
            inline=False
        )
        embed.add_field(
            name="&top marriage",
            value="Ver todas las parejas registradas",
            inline=False
        )
        return embed
    
    def _moderation_help(self):
        embed = discord.Embed(
            title="⚙️ COMANDOS DE MODERACIÓN",
            color=discord.Color.red(),
            description="Modera el servidor (requiere permisos)"
        )
        embed.add_field(
            name="&warn <usuario> [razón]",
            value="Advierte a un usuario (3 = kick automático)",
            inline=False
        )
        embed.add_field(
            name="&mute <usuario> <segundos> [razón]",
            value="Silencia a un usuario temporalmente",
            inline=False
        )
        embed.add_field(
            name="&kick <usuario> [razón]",
            value="Expulsa a un usuario del servidor",
            inline=False
        )
        embed.add_field(
            name="&ban <usuario> [razón]",
            value="Banea a un usuario del servidor",
            inline=False
        )
        embed.add_field(
            name="&unban <id> [razón]",
            value="Desbanea a un usuario",
            inline=False
        )
        embed.add_field(
            name="&warns [usuario]",
            value="Ve las advertencias de un usuario",
            inline=False
        )
        return embed
    
    def _admin_help(self):
        embed = discord.Embed(
            title="🔧 COMANDOS DE ADMIN",
            color=discord.Color.dark_red(),
            description="Solo para el dueño del bot"
        )
        embed.add_field(
            name="&reload <cog>",
            value="Recarga un cog (módulo) del bot",
            inline=False
        )
        embed.add_field(
            name="&addcoins <usuario> <monto>",
            value="Agrega coins a un usuario (testing)",
            inline=False
        )
        embed.add_field(
            name="&creacolores",
            value="Crea los 30 roles de colores",
            inline=False
        )
        embed.add_field(
            name="&autorroles",
            value="Muestra el menú para seleccionar color",
            inline=False
        )
        return embed

async def setup(bot):
    await bot.add_cog(Help(bot))
