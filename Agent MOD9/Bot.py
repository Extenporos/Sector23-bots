import discord
from discord.ext import commands
import json
import os

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
GUILD_ID = config.get("GUILD_ID")
PREFIX = config.get("PREFIX", "!")

intents = discord.intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    print(f"✅ Agent MOD9 conectado como {bot.user}")
    try:
        if GUILD_ID:
            await tree.sync(guild=discord.Object(id=GUILD_ID))
            print(f"🧩 Comandos slash (/) sincronizados con el servidor: {GUILD_ID}")
        else:
            await tree.sync()
            print("🧩 Comandos slash (/) sincronizados globalmente.")
    except Exeption as e:
        print(f"❌ Error al sincronizar comandos slash (/): {e}")

@bot.event
async def setup_hook():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"📦 COG cargado: {filename}")
bot.run(TOKEN)