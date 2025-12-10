from discord.ext import commands
import json, os

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "data/economy.json"
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
        user_id = ctx.author.id
        daily_file = "data/daily.json"
        
        if os.path.exists(daily_file):
            with open(daily_file) as f:
                daily_data = json.load(f)
        else:
            daily_data = {}
        
        import time
        last_daily = daily_data.get(str(user_id), 0)
        now = int(time.time())
        
        if now - last_daily < 86400:
            await ctx.send("❌ Ya recibiste tu daily hoy")
            return
        
        current = self.get_balance(user_id)
        self.set_balance(user_id, current + 500)
        
        daily_data[str(user_id)] = now
        with open(daily_file, "w") as f:
            json.dump(daily_data, f)
        
        await ctx.send("✅ Recibiste **500 coins** de tu daily!")

async def setup(bot):
    await bot.add_cog(Economy(bot))
