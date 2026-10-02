# **Zippy: un bot discord**.
Zippy è un bot discord in grado di eseguire innumerevoli attività quali: riprodurre musica o generare una password casuale.
Dispone inoltre di un configuratore di permessi, dove è possibile limitare l'uso di certe funzioni o bloccarle.
#### <p align="center"> [Informazioni sul codice](#informazioni-sul-codice) • [Permessi del bot](#come-funzionano-i-permessi-e-come-configurarli) • [File backlog](#cè-un-file-backlog) </p> 

## Informazioni sul codice
> [!NOTE]
> Il bot è diviso in 3 file principali, ma la struttura non è sempre coerente.

Questo progetto è diviso in tre file principali: [bot.py](bot.py), [bot_utils.py](bot_utils.py) e [configen.py](configen.py).\
Ciascuno contiene e svolge precise funzioni, il file [bot.py](bot.py) contiene generalmente codice essenziale per avviare il bot e slash commands come:
```python
@tree.command(
    name="riprendi_musica",
    description="Riprendi la musica."
)
async def resume_music(interaction: discord.Interaction):
    if channel_playings:
        await resume_audio(interaction)
    else:
        await interaction.response.send_message("Non c'è alcuna canzone in riproduzione!", ephemeral=True)
```
Il file [bot_utils.py](bot_utils.py) contiene quasi tutti i corpi di ogni funzione chiamata, ad esempio:
```python
async def resume_audio(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    vc.resume()
    await interaction.response.send_message(f"Ripresa della riproduzione in {channel_playings['Channel_Name']} di {channel_playings['Title']}")
```
Infine, [configen.py](configen.py) contiene solamente funzioni dedite alla creazione, all'apertura, al caricamento e al salvataggio del file di configurazione dei permessi di ogni utente (vedi [Come funzionano i permessi e come configurarli](#come-funzionano-i-permessi-e-come-configurarli)).

## Come funzionano i permessi e come configurarli
Questo bot dispone di una protezione per singolo server, attraverso l'uso del comando `set_permissions`, specificando il nome della funzione (reperibile da `print_cmds`), il ruolo interessato e la scelta (`Sì`, `No`, `Nessuno`, `Tutti`), è possibile impostare permessi sulle funzioni utilizzabili per ogni ruolo. <br>
E' bene notare che **`Nessuno` e `Tutti`** sono speciali, ma è comunque necessario specificare un ruolo. **`Nessuno`**, rimuove ogni ruolo impostato in una certa funzione, e inserisce `-1`, quando qualcuno proverà ad utilizzare la funzione interessata, non potrà farlo. `Tutti` rimuove ogni cosa che c'è nelle parentesi quadre, e la funzione è utilizzabile da tutti. <br>
`Sì` e `No` indicano rispettivamente se un certo ruolo è, o non è autorizzato ad usare quella funzione, solo i ruoli all'interno delle parentesi quadre di ogni funzione del file `.botconfig` sono autorizzate ad usare quella funzione, ad eccetto se c'è `-1` o se sono vuote. <br>
Non è possibile negare ad un ruolo di usare una funzione, il sistema è progettato per ragionare per _inclusione_ e non per _esclusione_. <br>
> [!NOTE]
> Ogni funzione non dichiarata in `.botconfig` con `set_permissions` è automaticamente considerata disponibile per **tutti**.

Questo è un file d'esempio che sarà sempre chiamato `.botconfig`. 
```json
{
  "permissions": {
    "eliminazione_messaggi_di_massa": [
      1553504518690447552
    ],
    "testa_o_croce": [
        "-1"
    ],
    "genera_password": []
  }
}
```

## C'è un file backlog?
Sì! C'è un file [backlog](backlog.md) dove è possibile vedere le attività future, completate e in corso. <br> Le attività sono divise in due sezioni: le [**Attività**](backlog.md#attivita-svoltein-corso) e le [**Attività Programmate**](backlog.md#attivita-programmate), nella prima sezione ci sono solo le attività completate e in corso cioè compiti che _dovrebbero essere completati_ entro il prossimo commit. <br> Nella seconda sezione ci sono modifiche programmate che possono avvenire in qualsiasi momento, è bene notare che possono anche essere completate da un commit all'altro, oppure possono essere inserite nella prima sezione per un vicino completamento.

