import discord
from discord.ui import View, Button
from utils.colors import COLORS

# --- Embed Factories ---

def simple_embed(title: str, description: str, color: discord.Color = discord.Color.blurple(), image_url: str = None, thumbnail_url: str = None, footer_text: str = None) -> discord.Embed:
    """Crea un embed básico con opciones comunes"""
    embed = discord.Embed(title=title, description=description, color=color)
    if image_url:
        embed.set_image(url=image_url)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if footer_text:
        embed.set_footer(text=footer_text)
    return embed

def success_embed(description: str) -> discord.Embed:
    """Embed verde para éxitos"""
    return simple_embed("✅ Éxito", description, color=discord.Color.green())

def error_embed(description: str) -> discord.Embed:
    """Embed rojo para errores"""
    return simple_embed("❌ Error", description, color=discord.Color.red())

def info_embed(title: str, description: str) -> discord.Embed:
    """Embed azul para información"""
    return simple_embed(title, description, color=discord.Color.blue())

# --- Reusable Views ---

class ConfirmView(View):
    """Vista con botones de Confirmar (Verde) y Cancelar (Rojo)"""
    def __init__(self, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.value = None

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.green, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ No puedes interactuar con este botón", ephemeral=True)
            return
        
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ No puedes interactuar con este botón", ephemeral=True)
            return
        
        self.value = False
        self.stop()
        await interaction.response.defer()

class AcceptDenyView(View):
    """Vista para aceptar/rechazar una propuesta (específico para target_user)"""
    def __init__(self, target_user, timeout=60):
        super().__init__(timeout=timeout)
        self.target_user = target_user
        self.value = None

    @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green, emoji="💍")
    async def accept(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.target_user:
            await interaction.response.send_message("❌ Esta propuesta no es para ti", ephemeral=True)
            return
        
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="💔")
    async def deny(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.target_user:
            await interaction.response.send_message("❌ Esta propuesta no es para ti", ephemeral=True)
            return
        
        self.value = False
        self.stop()
        await interaction.response.defer()

class PaginatorView(View):
    """Vista para paginación de embeds"""
    def __init__(self, embeds, timeout=60):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self._update_buttons()

    def _update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1
        self.page_counter.label = f"{self.current_page + 1}/{len(self.embeds)}"

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="1/1", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_counter(self, interaction: discord.Interaction, button: Button):
        pass

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            # Intentar editar el mensaje si tenemos acceso, pero no es crítico
            pass
        except:
            pass
