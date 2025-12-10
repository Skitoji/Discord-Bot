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
    
    @commands.command()
    async def perfil(self, ctx, user=None):
        """Ver perfil con nivel y XP"""
        if user:
            try:
                user = await commands.MemberConverter().convert(ctx, user)
                user_id = str(user.id)
            except:
                await ctx.send("❌ Usuario no encontrado")
                return
        else:
            user = ctx.author
            user_id = str(user.id)
        
        data = self.xp_data.get(user_id, {"xp": 0, "level": 1})
        level = data["level"]
        xp = data["xp"]
        nxt = self.xp_to_next(level)
        
        embed = __import__('discord').Embed(
            title=f"Perfil de {user}",
            color=__import__('discord').Color.blurple()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="⭐ Nivel", value=str(level))
        embed.add_field(name="✨ XP", value=f"{xp}/{nxt}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(XP(bot))
