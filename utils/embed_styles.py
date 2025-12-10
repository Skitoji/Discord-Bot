import discord

def simple(title, desc, color=discord.Color.random()):
    embed = discord.Embed(title=title, description=desc, color=color)
    return embed
