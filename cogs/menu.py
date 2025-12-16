import discord
from discord import app_commands
from discord.ext import commands

class MenuView(discord.ui.View):
    def __init__(self, help_cog):
        super().__init__(timeout=120)
        self.help_cog = help_cog

    @discord.ui.button(label="Música", style=discord.ButtonStyle.primary)
    async def music_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=self.help_cog._music_help(), ephemeral=True)

    @discord.ui.button(label="Economía", style=discord.ButtonStyle.success)
    async def economy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=self.help_cog._economy_help(), ephemeral=True)

    @discord.ui.button(label="Diversión", style=discord.ButtonStyle.secondary)
    async def fun_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=self.help_cog._fun_help(), ephemeral=True)

    @discord.ui.button(label="Perfil", style=discord.ButtonStyle.secondary)
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=self.help_cog._profile_help(), ephemeral=True)

    @discord.ui.button(label="Leaderboards", style=discord.ButtonStyle.secondary)
    async def leaderboards_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=self.help_cog._leaderboards_help(), ephemeral=True)

    @discord.ui.button(label="Moderación", style=discord.ButtonStyle.danger)
    async def moderation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=self.help_cog._moderation_help(), ephemeral=True)

    @discord.ui.button(label="Admin", style=discord.ButtonStyle.danger)
    async def admin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=self.help_cog._admin_help(), ephemeral=True)

class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_cog = bot.get_cog("Help")

    @app_commands.command(name="menu", description="Menú moderno de comandos")
    async def menu(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Menú de Comandos",
            description="Selecciona una categoría para ver los comandos disponibles.",
            color=discord.Color.blurple()
        )
        view = MenuView(self.help_cog)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def cog_load(self):
        # self.bot.tree.add_command(self.menu) # Duplicate registration
        pass

async def setup(bot):
    if bot.get_cog("Menu") is not None:
        print("⚠️ Cog 'Menu' ya cargado - omitiendo carga duplicada")
        return
    await bot.add_cog(Menu(bot))
