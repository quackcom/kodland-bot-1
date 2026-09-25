import os, random
import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from bot_utils import *

# la variabile intents contiene i permessi al bot
intents = discord.Intents.default()
# abilita il permesso a leggere i contenuti dei messaggi
intents.message_content = True
# crea un bot e passa gli indents
client = discord.Client(intents=intents, status=discord.Status.online, activity=discord.Game(onlineMessageCycle())) 
# crea un albero dei comandi
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'Abbiamo fatto l\'accesso come {client.user}')
    await tree.sync()  # sincronizza i comandi con Discord
    update_status.start()  # avvia il ciclo di aggiornamento dello stato
    print("Il bot è pronto e i comandi sono stati sincronizzati con Discord.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower().startswith('ciao') or message.content.lower().startswith('salve'):
        await message.channel.send(f"\U0001f642 {random.choice(possible_messages_benvenuto)}")
    elif message.content.lower().startswith('arrivederci'):
        await message.channel.send(f"\U0001f642 {random.choice(possible_messages_arrivederci)}")

@tree.command(
    name = "genera_password",
    description = "Genera una password casuale"
)
async def genera_password(interaction: discord.Interaction, lunghezza: int = 16):
    pass_length = lunghezza  # lunghezza della password
    password = gen_pass(pass_length)
    if len(password) > 2000 - 12:
        await interaction.response.send_message("La password generata è troppo lunga!", ephemeral=True)
        return
    await interaction.response.send_message(f"La password generata è: {password}", ephemeral=True)

@tasks.loop(seconds=300)  # aggiorna lo stato ogni 5 minuti
async def update_status():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(onlineMessageCycle()))

load_dotenv()

client.run(os.getenv("discord_tk"))