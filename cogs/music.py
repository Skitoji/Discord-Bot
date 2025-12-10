from discord.ext import commands
import discord
import yt_dlp
import asyncio
from collections import deque
import requests
import re
import os
import subprocess

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = deque()
        self.is_playing = False
        
        # Buscar FFmpeg
        self.ffmpeg_path = self._find_ffmpeg()
        
        # Opciones para yt-dlp
        self.ytdl_options = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'ytsearch',
            'quiet': True,
            'no_warnings': True,
        }
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_options)
    
    def _find_ffmpeg(self):
        """Buscar FFmpeg en rutas comunes"""
        possible_paths = [
            # Windows
            "C:\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            # Linux (Replit)
            "/usr/bin/ffmpeg",
            "/nix/store/*/bin/ffmpeg",
            # PATH
            "ffmpeg",
        ]
        
        for path in possible_paths:
            if path == "ffmpeg":
                try:
                    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                    print(f"✅ FFmpeg encontrado en PATH")
                    return "ffmpeg"
                except:
                    continue
            elif os.path.exists(path):
                print(f"✅ FFmpeg encontrado en: {path}")
                return path
        
        print("⚠️ FFmpeg no encontrado")
        return None
    
    def detect_platform(self, query):
        """Detectar la plataforma"""
        if 'spotify.com' in query:
            return 'spotify'
        elif 'music.apple.com' in query or 'itunes.apple.com' in query:
            return 'apple_music'
        elif 'youtube.com' in query or 'youtu.be' in query:
            return 'youtube'
        else:
            return 'search'
    
    async def get_spotify_info(self, url):
        """Extraer información de Spotify"""
        try:
            try:
                response = requests.get(url, timeout=5)
                title_match = re.search(r'og:title" content="([^"]+)"', response.text)
                if title_match:
                    title = title_match.group(1)
                    audio = await self.get_audio_url(title)
                    if audio:
                        return audio
            except:
                pass
            audio = await self.get_audio_url(url)
            return audio
        except Exception as e:
            return None
    
    async def get_apple_music_info(self, url):
        """Extraer información de Apple Music"""
        try:
            try:
                response = requests.get(url, timeout=5)
                title_match = re.search(r'og:title" content="([^"]+)"', response.text)
                if title_match:
                    title = title_match.group(1)
                    audio = await self.get_audio_url(title)
                    if audio:
                        return audio
            except:
                pass
            audio = await self.get_audio_url(url)
            return audio
        except Exception as e:
            return None
    
    async def get_audio_url(self, search):
        """Buscar en YouTube"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(search, download=False))
            
            if 'entries' in data:
                data = data['entries'][0]
            
            return {
                'url': data['url'],
                'title': data.get('title', 'Canción desconocida'),
                'duration': data.get('duration', 0),
                'thumbnail': data.get('thumbnail', '')
            }
        except Exception as e:
            return None
    
    async def play_audio(self, ctx, url, title):
        """Reproducir audio"""
        try:
            if not ctx.author.voice:
                await ctx.send("❌ Necesitas estar en un canal de voz")
                return
            
            if not self.ffmpeg_path:
                await ctx.send("❌ FFmpeg no está instalado. No puedo reproducir música.")
                return
            
            channel = ctx.author.voice.channel
            
            if ctx.voice_client is None or not ctx.voice_client.is_connected():
                await channel.connect()
            
            audio_source = discord.FFmpegPCMAudio(
                url,
                executable=self.ffmpeg_path,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn"
            )
            
            if not ctx.voice_client.is_playing():
                ctx.voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                self.is_playing = True
                await ctx.send(f"🎵 Reproduciendo: **{title}**")
            else:
                self.queue.append({'url': url, 'title': title})
                await ctx.send(f"➕ Añadido a cola: **{title}**")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
    
    async def play_next(self, ctx):
        """Siguiente canción"""
        if self.queue:
            next_song = self.queue.popleft()
            await self.play_audio(ctx, next_song['url'], next_song['title'])
        else:
            self.is_playing = False
    
    @commands.command()
    async def play(self, ctx, *, query):
        """Reproducir una canción"""
        platform = self.detect_platform(query)
        await ctx.send(f"🔍 Buscando en {platform.replace('_', ' ')}...")
        
        audio = None
        if platform == 'spotify':
            audio = await self.get_spotify_info(query)
        elif platform == 'apple_music':
            audio = await self.get_apple_music_info(query)
        else:
            audio = await self.get_audio_url(query)
        
        if audio:
            await self.play_audio(ctx, audio['url'], audio['title'])
        else:
            await ctx.send("❌ No se encontró la canción")
    
    @commands.command()
    async def pause(self, ctx):
        """Pausar"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Pausa")
        else:
            await ctx.send("❌ No hay música")
    
    @commands.command()
    async def resume(self, ctx):
        """Reanudar"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Reanudado")
        else:
            await ctx.send("❌ No hay música pausada")
    
    @commands.command()
    async def stop(self, ctx):
        """Detener"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.queue.clear()
            self.is_playing = False
            await ctx.send("⏹️ Detenido")
        else:
            await ctx.send("❌ No hay música")
    
    @commands.command()
    async def skip(self, ctx):
        """Saltar"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Saltado")
        else:
            await ctx.send("❌ No hay música")
    
    @commands.command()
    async def queue(self, ctx):
        """Ver cola"""
        if not self.queue:
            await ctx.send("📭 Cola vacía")
            return
        
        embed = discord.Embed(title="🎵 Cola", color=discord.Color.blurple())
        for i, song in enumerate(list(self.queue)[:10], 1):
            embed.add_field(name=f"#{i}", value=song['title'], inline=False)
        
        if len(self.queue) > 10:
            embed.set_footer(text=f"... y {len(self.queue) - 10} más")
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def disconnect(self, ctx):
        """Desconectar"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queue.clear()
            self.is_playing = False
            await ctx.send("👋 Desconectado")
        else:
            await ctx.send("❌ No estoy en un canal")

async def setup(bot):
    await bot.add_cog(Music(bot))
