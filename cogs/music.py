from discord.ext import commands
import discord
import yt_dlp
import asyncio
from collections import deque
import requests
import re
import os
import subprocess
from utils import ui

class MusicPlayerView(discord.ui.View):
    def __init__(self, ctx, music_cog):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.music_cog = music_cog
    
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.secondary)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.music_cog.is_playing:
             await interaction.response.send_message("❌ No hay música reproduciéndose", ephemeral=True)
             return
            
        voice_client = interaction.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("▶️ Reanudado", ephemeral=True)
        elif voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("⏸️ Pausado", ephemeral=True)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop()
            await interaction.response.send_message("⏭️ Saltado", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No hay música para saltar", ephemeral=True)
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client:
            self.music_cog.queue.clear()
            self.music_cog.is_playing = False
            voice_client.stop()
            await interaction.response.send_message("⏹️ Detenido y cola limpiada", ephemeral=True)
            self.stop() # Stop listening to interaction
        else:
            await interaction.response.send_message("❌ No estoy conectado", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = deque()
        self.is_playing = False
        
        # Buscar FFmpeg
        self.ffmpeg_path = self._find_ffmpeg()
        
        # Opciones para yt-dlp (formato 18 = MP4 sin descifrado requerido)
        self.ytdl_options = {
            'format': '18/best[ext=mp4]/best',
            'noplaylist': True,
            'default_search': 'ytsearch',
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 30,
            'skip_unavailable_fragments': True,
            'fragment_retries': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
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
            response = requests.get(url, timeout=5)
            title_match = re.search(r'og:title" content="([^"]+)"', response.text)
            if title_match:
                title = title_match.group(1)
                return await self.get_audio_url(title)
        except:
            pass
        # Si falla, intentar directo
        return await self.get_audio_url(url)
    
    async def get_apple_music_info(self, url):
        """Extraer información de Apple Music"""
        try:
            response = requests.get(url, timeout=5)
            title_match = re.search(r'og:title" content="([^"]+)"', response.text)
            if title_match:
                title = title_match.group(1)
                return await self.get_audio_url(title)
        except:
            pass
        # Si falla, intentar directo
        return await self.get_audio_url(url)
    
    async def get_audio_url(self, search):
        """Buscar en YouTube - Usando formato 18 (MP4 sin descifrado)"""
        try:
            loop = asyncio.get_event_loop()
            
            print(f"🔍 Buscando: {search}")
            
            # Opciones para obtener formato 18 (MP4 sin necesidad de descifrado de JS)
            ytdl_options = {
                'format': '18/best[ext=mp4]/best[ext=webm]',
                'noplaylist': True,
                'default_search': 'ytsearch',
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 30,
                'skip_unavailable_fragments': True,
                'fragment_retries': 3,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }
            
            ytdl = yt_dlp.YoutubeDL(ytdl_options)
            
            # Una sola búsqueda
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
            
            if not data:
                return None
            
            if 'entries' in data:
                data = data['entries'][0]
            
            # Buscar URL válida
            url = data.get('url')
            
            if not url:
                return None
            
            print(f"✅ Encontrada: {data.get('title', 'Canción desconocida')}")
            
            return {
                'url': url,
                'title': data.get('title', 'Canción desconocida'),
                'duration': data.get('duration', 0),
                'thumbnail': data.get('thumbnail', '')
            }
        except Exception as e:
            print(f"❌ Error en búsqueda: {search} - {str(e)[:100]}")
            return None
    
    async def play_audio(self, ctx, url, title):
        """Reproducir audio"""
        try:
            if not ctx.author.voice:
                await ctx.send(embed=ui.error_embed("Necesitas estar en un canal de voz"))
                return
            
            if not self.ffmpeg_path:
                await ctx.send(embed=ui.error_embed("FFmpeg no está instalado. No puedo reproducir música."))
                return
            
            channel = ctx.author.voice.channel
            
            if ctx.voice_client is None or not ctx.voice_client.is_connected():
                await channel.connect()
            
            # Usar FFmpegOpusAudio para mejor compatibilidad en Replit
            before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 -nostdin -hide_banner -loglevel error"
            options = "-vn -acodec libopus -ar 48000 -ac 2 -b:a 128k"
            
            audio_source = discord.FFmpegOpusAudio(
                url,
                executable=self.ffmpeg_path,
                before_options=before_options,
                options=options
            )
            
            if not ctx.voice_client.is_playing():
                ctx.voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                self.is_playing = True
                
                self.current_song = {'title': title, 'url': url}
                embed = ui.simple_embed("🎵 Reproduciendo", f"**{title}**", color=discord.Color.green())
                view = MusicPlayerView(ctx, self)
                await ctx.send(embed=embed, view=view)
            else:
                self.queue.append({'url': url, 'title': title})
                await ctx.send(embed=ui.info_embed("➕ Añadido a cola", f"**{title}**"))
        except Exception as e:
            await ctx.send(embed=ui.error_embed(f"Error: {e}"))
    
    async def play_next(self, ctx):
        """Siguiente canción"""
        if self.queue:
            next_song = self.queue.popleft()
            await self.play_audio(ctx, next_song['url'], next_song['title'])
        else:
            self.is_playing = False
    
    @commands.hybrid_command(description="Reproduce una canción/video")
    async def play(self, ctx, *, query: str):
        """Reproducir una canción"""
        platform = self.detect_platform(query)
        msg = await ctx.send(embed=ui.info_embed("🔍 Buscando...", f"Buscando en {platform.replace('_', ' ')}..."))
        
        audio = None
        if platform == 'spotify':
            audio = await self.get_spotify_info(query)
        elif platform == 'apple_music':
            audio = await self.get_apple_music_info(query)
        else:
            audio = await self.get_audio_url(query)
        
        await msg.delete()
        
        if audio:
            await self.play_audio(ctx, audio['url'], audio['title'])
        else:
            await ctx.send(embed=ui.error_embed("No se encontró la canción"))
    
    @commands.hybrid_command(description="Pausa la reproducción actual")
    async def pause(self, ctx):
        """Pausar"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send(embed=ui.info_embed("⏸️ Pausa", "Música pausada"))
        else:
            await ctx.send(embed=ui.error_embed("No hay música reproduciéndose"))
    
    @commands.hybrid_command(description="Reanuda la reproducción pausada")
    async def resume(self, ctx):
        """Reanudar"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send(embed=ui.success_embed("▶️ Reanudado"))
        else:
            await ctx.send(embed=ui.error_embed("No hay música pausada"))
    
    @commands.hybrid_command(description="Detiene el bot y limpia la cola")
    async def stop(self, ctx):
        """Detener"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.queue.clear()
            self.is_playing = False
            await ctx.send(embed=ui.error_embed("⏹️ Detenido"))
        else:
            await ctx.send(embed=ui.error_embed("No hay música"))
    
    @commands.hybrid_command(description="Salta a la siguiente canción")
    async def skip(self, ctx):
        """Saltar"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send(embed=ui.success_embed("⏭️ Saltado"))
        else:
            await ctx.send(embed=ui.error_embed("No hay música"))
    
    @commands.hybrid_command(description="Desconecta el bot del canal")
    async def disconnect(self, ctx):
        """Desconectar"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queue.clear()
            self.is_playing = False
            await ctx.send(embed=ui.success_embed("👋 Desconectado"))
        else:
            await ctx.send(embed=ui.error_embed("No estoy en un canal"))
    
    @commands.hybrid_command(description="Muestra la cola de reproducción")
    async def queue(self, ctx):
        """Ver cola de canciones"""
        if not self.queue:
            await ctx.send(embed=ui.info_embed("📭 Cola vacía", "No hay canciones en cola"))
            return
        
        embed = discord.Embed(
            title="🎵 Cola de reproducción",
            color=discord.Color.blue()
        )
        
        for i, song in enumerate(list(self.queue)[:10], 1):
            embed.add_field(
                name=f"{i}. {song['title'][:50]}",
                value=f"Duración: {song.get('duration', 'N/A')}s",
                inline=False
            )
        
        if len(self.queue) > 10:
            embed.set_footer(text=f"+{len(self.queue) - 10} canciones más")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(description="Muestra la canción actual")
    async def nowplaying(self, ctx):
        """Ver qué está sonando"""
        if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            if hasattr(self, 'current_song'):
                embed = ui.simple_embed(
                    "🎵 Reproduciendo",
                    self.current_song['title'],
                    color=discord.Color.blue()
                )
                # Show controls again
                view = MusicPlayerView(ctx, self)
                await ctx.send(embed=embed, view=view)
            else:
                 await ctx.send(embed=ui.info_embed("🎵 Info", "Reproduciendo música..."))
        else:
            await ctx.send(embed=ui.error_embed("No hay música sonando"))
    
    @commands.hybrid_command(description="Activa o desactiva la repetición")
    async def loop(self, ctx):
        """Repetir canción/cola"""
        if not hasattr(self, 'loop_enabled'):
            self.loop_enabled = False
        
        self.loop_enabled = not self.loop_enabled
        status = "🔄 Loop ACTIVADO" if self.loop_enabled else "❌ Loop desactivado"
        await ctx.send(embed=ui.info_embed("Loop", status))

async def setup(bot):
    if bot.get_cog("Music") is not None:
        return
    await bot.add_cog(Music(bot))
