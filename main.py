import discord
from discord.ext import commands
import os, json
import subprocess

# Verificar FFmpeg
def check_ffmpeg():
    """Verificar si FFmpeg está instalado"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg encontrado")
            return True
    except:
        pass
    
    print("⚠️ FFmpeg no encontrado. Intenta instalarlo manualmente desde:")
    print("   https://ffmpeg.org/download.html")
    return False

# Cargar configuración
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
PREFIX = config["PREFIX"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Pasar configuración al bot
bot.config = config

# Cargar automáticamente todos los cogs
async def load_cogs():
    cogs_dir = "./cogs"
    for file in os.listdir(cogs_dir):
        if file.endswith(".py") and not file.startswith("__"):
            try:
                cog_name = file[:-3]
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"⚙ Cog cargado → {file}")
            except Exception as e:
                print(f"❌ Error cargando {file}: {e}")

@bot.event
async def on_ready():
    print(f"\n🚀 Bot iniciado como {bot.user}\n")
    check_ffmpeg()

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())
