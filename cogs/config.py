import discord
from discord.ext import commands
from discord import app_commands, ui
import json
import os

WELCOME_CONFIG_FILE = "data/welcome_config.json"

def load_welcome_config():
    if os.path.exists(WELCOME_CONFIG_FILE):
        with open(WELCOME_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_welcome_config(data):
    with open(WELCOME_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

class TextModal(ui.Modal):
    def __init__(self, title, key, current_value, callback_func):
        super().__init__(title=title)
        self.key = key
        self.callback_func = callback_func
        
        self.text_input = ui.TextInput(
            label="Nuevo valor",
            style=discord.TextStyle.paragraph,
            default=current_value,
            max_length=1000,
            required=True
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        config = load_welcome_config()
        config[self.key] = self.text_input.value
        save_welcome_config(config)
        await interaction.response.send_message(f"✅ {self.key} actualizado!", ephemeral=True)
        await self.callback_func(interaction)

class ImageModal(ui.Modal):
    def __init__(self, current_url, callback_func):
        super().__init__(title="Editar Imagen de Bienvenida")
        self.callback_func = callback_func
        
        self.url_input = ui.TextInput(
            label="URL de la imagen/GIF",
            style=discord.TextStyle.short,
            default=current_url,
            placeholder="https://...",
            required=True
        )
        self.add_item(self.url_input)

    async def on_submit(self, interaction: discord.Interaction):
        config = load_welcome_config()
        config['welcome_image'] = self.url_input.value
        save_welcome_config(config)
        await interaction.response.send_message("✅ Imagen actualizada!", ephemeral=True)
        await self.callback_func(interaction)

class ChannelSelect(ui.ChannelSelect):
    def __init__(self, callback_func):
        super().__init__(
            placeholder="Selecciona el canal de bienvenida",
            channel_types=[discord.ChannelType.text]
        )
        self.callback_func = callback_func

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        config = load_welcome_config()
        config['channel_id'] = channel.id
        save_welcome_config(config)
        await interaction.response.send_message(f"✅ Canal de bienvenida establecido a {channel.mention}", ephemeral=True)
        await self.callback_func(interaction)

class WelcomeConfigView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ChannelSelect(self.refresh_embed))

    async def refresh_embed(self, interaction: discord.Interaction):
        # Helper to refresh the dashboard message if possible
        # Since interaction responses are handled locally in components, 
        # doing a full refresh of the original message is tricky without passing interaction context carefully.
        # For now, we rely on the ephemeral confirmations.
        pass

    @ui.button(label="Editar Título", style=discord.ButtonStyle.primary, row=1)
    async def edit_title(self, interaction: discord.Interaction, button: ui.Button):
        config = load_welcome_config()
        modal = TextModal("Editar Título", "welcome_title", config.get("welcome_title", ""), self.refresh_embed)
        await interaction.response.send_modal(modal)

    @ui.button(label="Editar Descripción", style=discord.ButtonStyle.primary, row=1)
    async def edit_desc(self, interaction: discord.Interaction, button: ui.Button):
        config = load_welcome_config()
        modal = TextModal("Editar Descripción", "welcome_description", config.get("welcome_description", ""), self.refresh_embed)
        await interaction.response.send_modal(modal)

    @ui.button(label="Editar Footer", style=discord.ButtonStyle.secondary, row=2)
    async def edit_footer(self, interaction: discord.Interaction, button: ui.Button):
        config = load_welcome_config()
        modal = TextModal("Editar Footer", "footer_text", config.get("footer_text", ""), self.refresh_embed)
        await interaction.response.send_modal(modal)

    @ui.button(label="Cambiar Imagen", style=discord.ButtonStyle.success, emoji="🖼️", row=2)
    async def edit_image(self, interaction: discord.Interaction, button: ui.Button):
        config = load_welcome_config()
        modal = ImageModal(config.get("welcome_image", ""), self.refresh_embed)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Probar Bienvenida", style=discord.ButtonStyle.danger, row=2)
    async def test_welcome(self, interaction: discord.Interaction, button: ui.Button):
        # Simular evento de bienvenida
        welcome_cog = interaction.client.get_cog("Welcome")
        if welcome_cog:
            await interaction.response.send_message("🔄 Enviando mensaje de prueba...", ephemeral=True)
            await welcome_cog.emit_test_welcome(interaction.user)
        else:
            await interaction.response.send_message("❌ Error: Cog 'Welcome' no cargado", ephemeral=True)

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Abre el panel de configuración del bot")
    @commands.has_permissions(administrator=True)
    async def dashboard(self, ctx):
        """Panel de configuración (Solo Admins)"""
        config = load_welcome_config()
        
        embed = discord.Embed(
            title="🛠️ Dashboard de Configuración",
            description="Configura el sistema de bienvenidas aquí. Usa los botones de abajo para editar.",
            color=discord.Color.dark_grey()
        )
        
        preview = (
            f"**Canal:** <#{config.get('channel_id', 'No configurado')}>\n"
            f"**Título:** {config.get('welcome_title')}\n"
            f"**Imagen:** [Link]({config.get('welcome_image')})"
        )
        embed.add_field(name="Configuración Actual", value=preview)
        
        await ctx.send(embed=embed, view=WelcomeConfigView())

async def setup(bot):
    await bot.add_cog(Config(bot))
