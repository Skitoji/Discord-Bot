from discord.ext import commands
import json, os, random

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "data/xp.json"
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file) as f:
                self.xp_data = json.load(f)
        else:
            self.xp_data = {}
    
    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.xp_data, f, indent=2)
    
    def xp_to_next(self, level):
        return 100 + (level - 1) * 50
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        user_id = str(message.author.id)
        if user_id not in self.xp_data:
            self.xp_data[user_id] = {"xp": 0, "level": 1}
        
        gain = random.randint(8, 15)
        self.xp_data[user_id]["xp"] += gain
        
        nxt = self.xp_to_next(self.xp_data[user_id]["level"])
        if self.xp_data[user_id]["xp"] >= nxt:
            self.xp_data[user_id]["xp"] -= nxt
            self.xp_data[user_id]["level"] += 1
            try:
                await message.channel.send(f"🎉 {message.author.mention} subió al nivel **{self.xp_data[user_id]['level']}**!")
            except:
                pass
        
        self.save_data()
    
    # @commands.command()
    # async def perfil(self, ctx, user=None):
    #     """(Deprecado) Ver perfil usando el comando /profile"""
    #     pass

async def setup(bot):
    if bot.get_cog("XP") is not None:
        print("⚠️ Cog 'XP' ya cargado - omitiendo carga duplicada")
        return
    await bot.add_cog(XP(bot))
