from discord.ext import commands, tasks
import discord
import json, os, time, random

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaways_file = "data/giveaways.json"
        self.load_giveaways()
        self.giveaway_checker.start()
    
    def load_giveaways(self):
        if os.path.exists(self.giveaways_file):
            with open(self.giveaways_file) as f:
                self.giveaways = json.load(f)
        else:
            self.giveaways = {}
    
    def save_giveaways(self):
        with open(self.giveaways_file, "w") as f:
            json.dump(self.giveaways, f, indent=2)
    
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def sorteo(self, ctx, minutos: int, *, premio: str):
        """Inicia un sorteo"""
        if minutos <= 0:
            await ctx.send("❌ El tiempo debe ser mayor a 0")
            return
        
        gw_id = f"gw_{ctx.guild.id}_{int(time.time())}"
        self.giveaways[gw_id] = {
            "prize": premio,
            "host": str(ctx.author.id),
            "channel_id": ctx.channel.id,
            "end_time": int(time.time()) + (minutos * 60),
            "ended": False
        }
        
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            color=discord.Color.gold()
        )
        embed.add_field(name="Premio", value=premio)
        embed.add_field(name="Duración", value=f"{minutos} minutos")
        embed.add_field(name="Host", value=ctx.author.mention)
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")
        
        self.giveaways[gw_id]["message_id"] = msg.id
        self.save_giveaways()
        
        await ctx.send(f"✅ Sorteo iniciado! Reacciona con 🎉 para participar")
    
    @tasks.loop(seconds=10)
    async def giveaway_checker(self):
        """Revisa sorteos vencidos"""
        now = int(time.time())
        
        for gw_id, gw_data in list(self.giveaways.items()):
            if gw_data.get("ended"):
                continue
            
            if now >= gw_data.get("end_time", 0):
                gw_data["ended"] = True
                
                try:
                    guild = self.bot.get_guild(int(gw_id.split("_")[1]))
                    channel = guild.get_channel(gw_data["channel_id"])
                    message = await channel.fetch_message(gw_data["message_id"])
                    
                    for reaction in message.reactions:
                        if reaction.emoji == "🎉":
                            participants = [user async for user in reaction.users() if not user.bot]
                            
                            if participants:
                                winner = random.choice(participants)
                                embed = discord.Embed(
                                    title="🎉 GANADOR 🎉",
                                    color=discord.Color.gold()
                                )
                                embed.add_field(name="Premio", value=gw_data["prize"])
                                embed.add_field(name="Ganador", value=winner.mention)
                                await channel.send(embed=embed)
                            else:
                                await channel.send("❌ No hubo participantes")
                except Exception as e:
                    print(f"Error en giveaway: {e}")
                
                self.save_giveaways()
    
    @giveaway_checker.before_loop
    async def before_giveaway_checker(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
