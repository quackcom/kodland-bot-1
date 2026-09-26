import random, yt_dlp, discord, asyncio

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

async def play_audio(interaction: discord.Interaction, url: str, channel_name: str):
    guild = interaction.guild

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
        'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -headers "User-Agent: {user_agent}"',
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
    vc.play(audio_source, after= lambda e: stop_audiosync(e, interaction)) # lambda e: print(f"ERRORE RIPRODUZIONE FFmpeg: {e}") if e else print("Riproduzione terminata con successo senza errori.")

    # Aggiorna la chat confermando la riproduzione
    channel_playings["Channel_Name"] = channel_name
    channel_playings["Title"] = title
    await interaction.followup.send(f"Riproduzione di {title} in {channel_name}")

async def stop_audio(interaction: discord.Interaction):
    title = channel_playings["Title"]
    channel_name = channel_playings["Channel_Name"]
    wasPlaying = False
    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        if vc.is_playing():
            wasPlaying = True
            vc.stop()
        await vc.disconnect()
        if wasPlaying == True:
            await interaction.response.send_message(f"Riproduzione terminata di {title} in {channel_name}")
            return
        
        await interaction.followup.send("Disconnesso dal canale vocale!")
    else:
        await interaction.response.send_message("Non sono connesso a nessun canale vocale in questo server.", ephemeral=True)

def stop_audiosync(error, interaction: discord.Interaction):
    if error:
        print(f"Errore riproduzione: {error}")
        return

    title = channel_playings.get("Title")
    channel_name = channel_playings.get("Channel_Name")
    vc = interaction.guild.voice_client
    bot_loop = interaction.client.loop

    async def _cleanup():
        was_connected = vc and vc.is_connected()
        if was_connected:
            await vc.disconnect()
            await interaction.followup.send(f"Riproduzione terminata di {title} in {channel_name}")

    asyncio.run_coroutine_threadsafe(_cleanup(), bot_loop)


def testa_o_croce(selezione: str) -> str:
    random_choice = random.choice(["head", "back"])

    if random_choice == selezione:
        return ("Complimenti! Hai vinto!")
    elif random_choice != selezione:
        return ("Che peccato, hai perso!")
