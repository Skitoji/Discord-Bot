from discord.ext import commands
import discord
import random
import aiohttp

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def eightball(self, ctx, *, question):
        """Bola 8 mágica - &eightball <pregunta>"""
        responses = [
            "Sí, definitivamente",
            "No, de ninguna manera",
            "Puede ser",
            "Pregunta de nuevo más tarde",
            "La respuesta es clara",
            "No cuentes con ello",
            "Seguramente",
            "Muy dudoso",
            "Sin duda",
            "El futuro es incierto"
        ]
        
        embed = discord.Embed(
            title="🔮 Bola Mágica",
            description=f"**Pregunta:** {question}\n\n**Respuesta:** {random.choice(responses)}",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def roulette(self, ctx):
        """Ruleta rusa - 50% de perder dinero (necesita cog economy)"""
        # Obtener balance de economy cog
        economy = self.bot.get_cog('Economy')
        if not economy:
            await ctx.send("❌ Economy cog no encontrado")
            return
        
        balance = economy.get_balance(ctx.author.id)
        
        if balance == 0:
            await ctx.send("❌ Necesitas dinero para jugar")
            return
        
        if random.random() > 0.5:
            loss = int(balance * 0.5)
            economy.set_balance(ctx.author.id, balance - loss)
            await ctx.send(f"💀 ¡PERDISTE! Perdiste **{loss}** coins")
        else:
            gain = int(balance * 0.5)
            economy.set_balance(ctx.author.id, balance + gain)
            await ctx.send(f"😱 ¡SOBREVIVISTE! Ganaste **{gain}** coins por tu valentía")
    
    @commands.command()
    async def trivia(self, ctx):
        """Pregunta de trivia aleatoria"""
        questions = [
            {"q": "¿Cuál es el planeta más grande del sistema solar?", "a": "jupiter"},
            {"q": "¿En qué año se inventó el internet?", "a": "1969"},
            {"q": "¿Cuál es la capital de Francia?", "a": "paris"},
            {"q": "¿Cuántos continentes hay?", "a": "7"},
            {"q": "¿En qué país se originó el tango?", "a": "argentina"},
            {"q": "¿Cuál es el río más largo del mundo?", "a": "nilo"},
            {"q": "¿En qué año cayó el Muro de Berlín?", "a": "1989"},
            {"q": "¿Cuántos lados tiene un hexágono?", "a": "6"},
        ]
        
        question = random.choice(questions)
        embed = discord.Embed(
            title="🧠 Trivia",
            description=question["q"],
            color=discord.Color.blue()
        )
        
        msg = await ctx.send(embed=embed)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=10)
            if answer.content.lower() == question["a"]:
                await ctx.send(f"✅ ¡Correcto! La respuesta era **{question['a']}**")
            else:
                await ctx.send(f"❌ Incorrecto. La respuesta era **{question['a']}**")
        except:
            await ctx.send(f"⏱️ Se acabó el tiempo. La respuesta era **{question['a']}**")
    
    @commands.command()
    async def meme(self, ctx):
        """Obtener meme aleatorio de Reddit"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as r:
                data = await r.json()
                
                embed = discord.Embed(
                    title=data['title'],
                    color=discord.Color.random()
                )
                embed.set_image(url=data['url'])
                embed.set_footer(text=f"👍 {data['ups']} | r/{data['subreddit']}")
                
                await ctx.send(embed=embed)
    
    @commands.command()
    async def flip(self, ctx):
        """Lanzar una moneda"""
        result = random.choice(['Cara ✅', 'Cruz ❌'])
        await ctx.send(f"🪙 {result}")
    
    @commands.command()
    async def roll(self, ctx, sides: int = 6):
        """Lanzar dado - &roll <caras>"""
        if sides < 2:
            await ctx.send("❌ El dado debe tener al menos 2 caras")
            return
        
        result = random.randint(1, sides)
        await ctx.send(f"🎲 Sacaste un **{result}** en un dado de {sides} caras")
    
    @commands.command()
    async def choose(self, ctx, *, options):
        """Elegir entre opciones - &choose opción1 | opción2 | opción3"""
        choices = [c.strip() for c in options.split('|')]
        
        if len(choices) < 2:
            await ctx.send("❌ Necesitas al menos 2 opciones separadas por |")
            return
        
        chosen = random.choice(choices)
        await ctx.send(f"🎯 Elegí: **{chosen}**")

async def setup(bot):
    await bot.add_cog(Fun(bot))
