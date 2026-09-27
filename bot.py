import os, random, discord
from discord import app_commands
from discord.ext import tasks, commands
from dotenv import load_dotenv
from bot_utils import *
from configen import *

# la variabile intents contiene i permessi al bot
intents = discord.Intents.default()
# abilita il permesso a leggere i contenuti dei messaggi
intents.message_content = True
# crea un bot e passa gli indents
bot = commands.Bot(intents=intents, status=discord.Status.online, activity=discord.Game(onlineMessageCycle()), command_prefix='$') 
# crea un albero dei comandi
tree = bot.tree # app_commands.CommandTree(bot)
# Dai i permessi di vedere i canali e le chat vocali.
intents.guilds = True
intents.voice_states = True

FUNZIONI_PROTEGGIBILI = []

@bot.event
async def on_ready():
    print(f'Abbiamo fatto l\'accesso come {bot.user}')
    await tree.sync()  # sincronizza i comandi con Discord
    update_status.start()  # avvia il ciclo di aggiornamento dello stato
    print("Il bot è pronto e i comandi sono stati sincronizzati con Discord.")

@bot.command()
async def ciao(ctx):
    await ctx.send(f"\U0001f642 {random.choice(possible_messages_benvenuto)}")

@bot.command()
async def arrivederci(ctx):
    await ctx.send(f"\U0001f642 {random.choice(possible_messages_arrivederci)}")

@bot.command() # to implement cmd tree
async def joined(ctx, member: discord.Member):
    await ctx.send(f'{member.name} joined our beautiful server at {discord.utils.format_dt(member.joined_at)}')

async def appFUNZIONI_PROTEGGIBILI():
    for command in tree.walk_commands():
        FUNZIONI_PROTEGGIBILI.append(command.name)

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

@tree.command(
    name= "riproduci_musica",
    description= "Riproduce musica nel canale scelto."
)
@app_commands.choices(
    to_loop = [
        app_commands.Choice(name="Sì", value="True"),
        app_commands.Choice(name="No", value="False")
    ]
)
async def play_music(interaction: discord.Interaction, url: str, channel_name: str, inizia_dal_secondo: int = 0, to_loop: app_commands.Choice[str] = None):
    is_loop_pass = to_loop.value if to_loop is not None else "False"
    await play_audio(interaction, url, channel_name, is_loop_pass, inizia_dal_secondo)

@tree.command(
    name= "ferma_musica",
    description= "Ferma la musica nel canale."
)
async def stop_music(interaction: discord.Interaction):
    await stop_audio(interaction)

@tree.command(
    name="pausa_musica",
    description="Metti in pausa la musica."
)
async def pause_music(interaction: discord.Interaction):
    if channel_playings:
        await pause_audio(interaction)
    else:
        await interaction.response.send_message("Non c'è alcuna canzone in riproduzione!", ephemeral=True)

@tree.command(
    name="riprendi_musica",
    description="Riprendi la musica."
)
async def resume_music(interaction: discord.Interaction):
    if channel_playings:
        await resume_audio(interaction)
    else:
        await interaction.response.send_message("Non c'è alcuna canzone in riproduzione!", ephemeral=True)

@tree.command(
    name= "testa_o_croce",
    description= "Testa o croce?"
)
@app_commands.choices(
    choose = [
        app_commands.Choice(name="Testa", value="head"),
        app_commands.Choice(name="Croce", value="back")
    ]
)
async def testa_croce_cmd(interaction: discord.Interaction, choose: app_commands.Choice[str]):
    scelta_giocatore = choose.value
    risultato = testa_o_croce(scelta_giocatore)
    await interaction.response.send_message(risultato, ephemeral=True)

@tree.command(
    name= "eliminazione_messaggi_di_massa",
    description="Elimina i messaggi in massa, a partire dal più recente."
)
@app_commands.describe(m_to_delete="Il numero di messaggi da eliminare.")
async def purge(interaction: discord.Interaction, m_to_delete: int):
    if not is_authorized(interaction.user, "eliminazione_messaggi_di_massa", config):
        await interaction.response.send_message("Non hai i permessi necessari per utilizzare questa funzione.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=m_to_delete)
    await interaction.followup.send(f"Sono stati eliminati {len(deleted)} messaggi.")

@tree.command(
    name="set_permissions",
    description="Imposta i permessi ad usare determinati programmi."
)
@app_commands.choices(
    funzioni = [
        app_commands.Choice(name=func, value=func) for func in FUNZIONI_PROTEGGIBILI
    ],
    scelta = [
        app_commands.Choice(name="Aggiungi", value="True"),
        app_commands.Choice(name="Rimuovi", value="False"),
        app_commands.Choice(name="Nessuno", value="None"),
        app_commands.Choice(name="Tutti", value="All")
    ]
)
async def set_permissions(interaction: discord.Interaction, funzioni: app_commands.Choice[str], ruolo: discord.Role, scelta: app_commands.Choice[str]):
    func_name = funzioni.value

    config.setdefault("permissions", {}).setdefault(func_name, [])

    # Registrazione
    if ruolo.id not in config["permissions"][func_name] and scelta.value == "True":
        if "-1" in config["permissions"][func_name]:
            config["permissions"][func_name].remove("-1")
        config["permissions"][func_name].append(ruolo.id)
        await interaction.response.send_message(f"Il ruolo {ruolo}, con id {ruolo.id} è stato abilitato ad usare la funzione {func_name} correttamente.", ephemeral=True)
    elif scelta.value == "True" and ruolo.id in config["permissions"][func_name]:
        await interaction.response.send_message(f"Questo ruolo è già registrato per questa funzione.", ephemeral=True)

    # Deregistrazione
    if ruolo.id in config["permissions"][func_name] and scelta.value == "False":
        config["permissions"][func_name].remove(ruolo.id)
        await interaction.response.send_message(f"Il ruolo {ruolo}, con id {ruolo.id} non può più usare la funzione {func_name}", ephemeral=True)
    elif "-1" in config["permissions"][func_name] and scelta.value == "False":
            await interaction.response.send_message(f"Devi prima registare qualcuno per {func_name}!", ephemeral=True)
            return
    elif scelta.value == "False" and ruolo.id not in config["permissions"][func_name]:
        await interaction.response.send_message(f"Questo ruolo è già NON-registrato per {func_name}.", ephemeral=True)

    # Deregistraione per nessuno
    if scelta.value == "None":
        for role in config["permissions"][func_name]:
            config["permissions"][func_name].remove(role)
        config["permissions"][func_name].append("-1")
        await interaction.response.send_message(f"Tutti i ruoli sono stati rimossi e l'uso di {func_name} è ora interdetto.", ephemeral=True)

    # Registrazione per tutti
    if scelta.value == "All":
        for role in config["permissions"][func_name]:
            config["permissions"][func_name].remove(role)
        await interaction.response.send_message(f"I permessi sono stati resettati e la funzione {func_name} è ora disponibile per tutti.", ephemeral=True)        

    save_config(config)

@tree.command(
    name="print_cmds",
    description="Mostra in chat tutti i comandi utilizzabili."
)
async def print_cmds(interaction: discord.Interaction):
    if len(FUNZIONI_PROTEGGIBILI) == 0:
        await appFUNZIONI_PROTEGGIBILI()
    elenco = "\n".join(f"`{nome}`" for nome in FUNZIONI_PROTEGGIBILI)
    await interaction.response.send_message(f"**Comandi disponibili:**\n{elenco}", ephemeral=True)

@tasks.loop(seconds=300)  # aggiorna lo stato ogni 5 minuti
async def update_status():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(onlineMessageCycle()))

load_dotenv()

bot.run(os.getenv("discord_tk"))