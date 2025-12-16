from discord.ext import commands
import json, os, random, time
import discord

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "data/economy.json"
        self.daily_file = "data/daily.json"
        self.weekly_file = "data/weekly.json"
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file) as f:
                self.economy = json.load(f)
        else:
            self.economy = {}
    
    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.economy, f, indent=2)
    
    def get_balance(self, user_id):
        return self.economy.get(str(user_id), 0)
    
    def set_balance(self, user_id, amount):
        self.economy[str(user_id)] = amount
        self.save_data()
    
    @commands.command()
    async def balance(self, ctx, user=None):
        """Ver balance de coins"""
        if user:
            try:
                user = await commands.MemberConverter().convert(ctx, user)
                user_id = user.id
                balance = self.get_balance(user_id)
                await ctx.send(f"💰 {user.mention} tiene **{balance}** coins")
            except:
                await ctx.send("❌ Usuario no encontrado")
        else:
            balance = self.get_balance(ctx.author.id)
            await ctx.send(f"💰 Tienes **{balance}** coins")
    
    @commands.command()
    async def daily(self, ctx):
        """Recibe 500 coins diarios"""
        user_id = str(ctx.author.id)
        
        if os.path.exists(self.daily_file):
            with open(self.daily_file) as f:
                daily_data = json.load(f)
        else:
            daily_data = {}
        
        last_daily = daily_data.get(user_id, 0)
        now = int(time.time())
        
        if now - last_daily < 86400:
            remaining = 86400 - (now - last_daily)
            hours = remaining // 3600
            await ctx.send(f"❌ Vuelve en {hours}h para tu daily")
            return
        
        current = self.get_balance(ctx.author.id)
        self.set_balance(ctx.author.id, current + 500)
        
        daily_data[user_id] = now
        with open(self.daily_file, "w") as f:
            json.dump(daily_data, f)
        
        await ctx.send("✅ Recibiste **500 coins** de tu daily!")
    
    @commands.command()
    async def weekly(self, ctx):
        """Recibe 2000 coins semanales"""
        user_id = str(ctx.author.id)
        
        if os.path.exists(self.weekly_file):
            with open(self.weekly_file) as f:
                weekly_data = json.load(f)
        else:
            weekly_data = {}
        
        last_weekly = weekly_data.get(user_id, 0)
        now = int(time.time())
        
        if now - last_weekly < 604800:
            remaining = 604800 - (now - last_weekly)
            days = remaining // 86400
            await ctx.send(f"❌ Vuelve en {days}d para tu weekly")
            return
        
        current = self.get_balance(ctx.author.id)
        self.set_balance(ctx.author.id, current + 2000)
        
        weekly_data[user_id] = now
        with open(self.weekly_file, "w") as f:
            json.dump(weekly_data, f)
        
        await ctx.send("✅ Recibiste **2000 coins** de tu weekly! 🎉")
    
    @commands.command()
    async def work(self, ctx):
        """Trabaja y gana coins"""
        earnings = random.randint(50, 200)
        current = self.get_balance(ctx.author.id)
        self.set_balance(ctx.author.id, current + earnings)
        
        messages = [
            f"🏭 Trabajaste y ganaste **{earnings}** coins",
            f"💼 Completaste un trabajo y obtuviste **{earnings}** coins",
            f"⛏️ Minaste y encontraste **{earnings}** coins"
        ]
        
        await ctx.send(random.choice(messages))
    
    @commands.command()
    async def gamble(self, ctx, amount: int):
        """Juega apostar (50% de ganar/perder)"""
        balance = self.get_balance(ctx.author.id)
        
        if amount <= 0:
            await ctx.send("❌ Apuesta un monto válido")
            return
        
        if amount > balance:
            await ctx.send(f"❌ No tienes suficientes coins")
            return
        
        if random.random() > 0.5:
            self.set_balance(ctx.author.id, balance + amount)
            await ctx.send(f"🎰 ¡GANASTE! +**{amount}** coins 🎉")
        else:
            self.set_balance(ctx.author.id, balance - amount)
            await ctx.send(f"🎰 Perdiste **{amount}** coins 😢")
    
    @commands.command()
    async def slots(self, ctx, amount: int):
        """Máquina tragamonedas"""
        balance = self.get_balance(ctx.author.id)
        
        if amount <= 0 or amount > balance:
            await ctx.send("❌ Apuesta inválida")
            return
        
        emojis = ['🍎', '🍊', '🍋', '🍌', '🍉']
        result = [random.choice(emojis) for _ in range(3)]
        
        self.set_balance(ctx.author.id, balance - amount)
        
        if result[0] == result[1] == result[2]:
            winnings = amount * 5
            self.set_balance(ctx.author.id, balance - amount + winnings)
            await ctx.send(f"🎰 {result[0]} {result[1]} {result[2]}\n🎉 ¡JACKPOT! +**{winnings}** coins!")
        elif result[0] == result[1] or result[1] == result[2]:
            winnings = amount * 2
            self.set_balance(ctx.author.id, balance - amount + winnings)
            await ctx.send(f"🎰 {result[0]} {result[1]} {result[2]}\n✨ ¡2 iguales! +**{winnings}** coins")
        else:
            await ctx.send(f"🎰 {result[0]} {result[1]} {result[2]}\n😢 -{amount} coins")
    
    @commands.command()
    async def pagar(self, ctx, user: discord.Member, amount: int):
        """Transferir coins a otro usuario"""
        balance = self.get_balance(ctx.author.id)
        
        if amount <= 0 or amount > balance:
            await ctx.send("❌ Monto inválido")
            return
        
        self.set_balance(ctx.author.id, balance - amount)
        receiver = self.get_balance(user.id)
        self.set_balance(user.id, receiver + amount)
        
        await ctx.send(f"✅ Enviaste **{amount}** coins a {user.mention}")
    
    @commands.command()
    async def leaderboard(self, ctx):
        """Ranking de coins"""
        sorted_users = sorted(
            self.economy.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        embed = discord.Embed(title="💰 Leaderboard", color=discord.Color.gold())
        
        for i, (user_id, balance) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                embed.add_field(name=f"#{i} {user.name}", value=f"{balance} coins", inline=False)
            except:
                pass
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.is_owner()
    async def addcoins(self, ctx, user: discord.Member, amount: int):
        """Agregar coins a un usuario (Solo owner)"""
        if amount < 0:
            await ctx.send("❌ Monto inválido")
            return
        
        current = self.get_balance(user.id)
        self.set_balance(user.id, current + amount)
        
        await ctx.send(f"✅ Agregaste **{amount}** coins a {user.mention}\nNuevo balance: {current + amount}")

async def setup(bot):
    if bot.get_cog("Economy") is not None:
        print("⚠️ Cog 'Economy' ya cargado - omitiendo carga duplicada")
        return
    await bot.add_cog(Economy(bot))
