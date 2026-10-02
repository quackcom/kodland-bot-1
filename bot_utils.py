import random, yt_dlp, discord, asyncio
from configen import *

possible_messages_activity = [
    "Playing with passwords",
    "Being useful",
    "Hello",
    "Generating passwords",
    "Helping users",
    "Monitoring messages",
    "Checking Zippy.py"
]

possible_messages_benvenuto = [
    "Ciao!",
    "Benvenuto!",
    "Ehilà!"
]

possible_messages_arrivederci = [
    "Ciao!",
    "Arrivederci!",
    "Ci si vede!"
]

# YTDL Config
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'extract_flat': False,
    'skip_download': True,
    'cookiefile': R"misc\cookies.txt" # scraped cookies to trick yt
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

config = load_config()

# FFMPEG PATH
FFMPEG_PATH = R"misc\ffmpeg.exe"

channel_playings = {}

def onlineMessageCycle():
    return random.choice(possible_messages_activity)

def gen_pass(pass_length):
    elements = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890+-/*!&$#?=@<>"
    password = ""

    for _ in range(pass_length):
        password += random.choice(elements)

    return password

async def play_audio(interaction: discord.Interaction, url: str, channel_name: str, is_loop_pass: str, inizia_dal_secondo: int = 0):
    guild = interaction.guild

    to_loop_song = True if is_loop_pass == "1" else False

    # Cerca il canale per nome o ID
    channel = discord.utils.get(guild.voice_channels, name=channel_name)
    if not channel:
        try:
            channel = guild.get_channel(int(channel_name))
        except ValueError:
            pass

    if channel is None or not isinstance(channel, discord.VoiceChannel):
        await interaction.response.send_message(f"Impossibile trovare il canale vocale: {channel_name}", ephemeral=True)
        return

    # Gestione connessione del bot al canale
    vc = guild.voice_client
    try:
        if not vc:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)
    except discord.ClientException as e:
        await interaction.response.send_message(f"Errore di connessione al canale vocale: {e}", ephemeral=True)
        return

    # Invia un messaggio per fare sapere all'utente che ha iniziato
    await interaction.response.send_message("Caricamento audio in corso...", ephemeral=True)

    # Estrazione dello streaming audio da YouTube
    try:
        data = ytdl.extract_info(url, download=False)
    except Exception as e:
        await interaction.followup.send(f"Errore durante l'estrazione: {e}", ephemeral=True)
        return

    http_headers = data.get('http_headers', {})
    user_agent = http_headers.get('User-Agent', 'Mozilla/5.0')

    FFMPEG_OPTIONS = {
        'before_options': f'-ss {inizia_dal_secondo} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -headers "User-Agent: {user_agent}"',
        'options': '-vn'
    }

    if 'entries' in data:
        data = data['entries'][0]

    filename = data['url']
    title = data.get('title', 'Audio')

    if vc.is_playing():
        vc.stop()

    # Avvio riproduzione FFmpeg
    audio_source = discord.FFmpegPCMAudio(filename, executable=FFMPEG_PATH, **FFMPEG_OPTIONS)
    vc.play(audio_source, after= lambda e: stop_audiounsync(e, interaction)) # lambda e: print(f"ERRORE RIPRODUZIONE FFmpeg: {e}") if e else print("Riproduzione terminata con successo senza errori.")

    # Aggiorna la chat confermando la riproduzione
    channel_playings["Channel_Name"] = channel_name
    channel_playings["Title"] = title
    if to_loop_song == True:
        inizia_dal_secondo = 0
        channel_playings["To_Loop_Bool"] = to_loop_song
        channel_playings["FFMPEG_OPTS"] = FFMPEG_OPTIONS
        channel_playings["URL"] = url
    await interaction.followup.send(f"Riproducendo {title} in {channel_name}")

async def stop_audio(interaction: discord.Interaction):
    try:
        title = channel_playings["Title"]
        channel_name = channel_playings["Channel_Name"]
    except Exception as e:
        pass
    wasPlaying = False
    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        if vc.is_playing():
            wasPlaying = True
            vc.stop()
        await vc.disconnect()
        if wasPlaying == True:
            await interaction.response.send_message(f"Riproduzione terminata di {title} in {channel_name}")
            channel_playings.clear()
            return
        
        await interaction.followup.send("Disconnesso dal canale vocale!")
    else:
        await interaction.response.send_message("Non sono connesso a nessun canale vocale in questo server.", ephemeral=True)

def stop_audiounsync(error, interaction: discord.Interaction):
    if error:
        print(f"Errore riproduzione: {error}")
        return

    title = channel_playings.get("Title")
    channel_name = channel_playings.get("Channel_Name")
    ffmpeg_options = channel_playings.get("FFMPEG_OPTS")
    to_loop_bool = channel_playings.get("To_Loop_Bool")
    url = channel_playings.get("URL")

    vc = interaction.guild.voice_client
    bot_loop = interaction.client.loop

    async def _cleanup_or_replay():
        if not (vc and vc.is_connected()):
            return

        if to_loop_bool == True:
            # Ri-estrazione del contenuto audio
            try:
                data = ytdl.extract_info(url, download=False)
            except Exception as e:
                await interaction.followup.send(f"Errore durante l'estrazione: {e}", ephemeral=True)
                return

            if 'entries' in data:
                data = data['entries'][0]

            filename = data['url']
            loop_audio_source = discord.FFmpegPCMAudio(filename, executable=FFMPEG_PATH, **ffmpeg_options)
            vc.play(loop_audio_source, after= lambda e: stop_audiounsync(e, interaction))
        else:
            await vc.disconnect()
            await interaction.followup.send(f"Riproduzione terminata di {title} in {channel_name}")
            channel_playings.clear()

    asyncio.run_coroutine_threadsafe(_cleanup_or_replay(), bot_loop)

async def pause_audio(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    vc.pause()
    await interaction.response.send_message(f"Riproduzione in pausa in {channel_playings['Channel_Name']} di {channel_playings['Title']}")

async def resume_audio(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    vc.resume()
    await interaction.response.send_message(f"Ripresa della riproduzione in {channel_playings['Channel_Name']} di {channel_playings['Title']}")

def testa_o_croce(selezione: str) -> str:
    dict_hb = {
        "head": "Testa",
        "back": "Croce"
    }
    random_choice = random.choice(["head", "back"])

    if random_choice == selezione:
        return (f"Complimenti! Hai vinto! E' uscito {dict_hb[random_choice]}")
    elif random_choice != selezione:
        return (f"Che peccato, hai perso! E' uscito {dict_hb[random_choice]}")

def is_authorized(member: discord.Member, funzione: str, config: dict) -> bool:
    ruoli_autorizzati = config.get("permissions", {}).get(funzione)
    if not ruoli_autorizzati:
        return True
    if "-1" in ruoli_autorizzati:
        return False
    member_role_ids = {r.id for r in member.roles}
    return any(rid in member_role_ids for rid in ruoli_autorizzati)
