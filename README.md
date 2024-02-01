# Content-generator-wordpress


Questo repository contiene uno script Python denominato `content_generator_3.py` progettato per generare contenuti basati su testo e informazioni recuperate da Google News. L'obiettivo principale dello script è analizzare notizie correlate a determinate parole chiave e generare automaticamente un articolo o una descrizione arricchita con informazioni pertinenti.

# Sviluppi
Il primo passo è fatto, ora stiamo sviluppando un sistema di content generator automatico con un'attivazione lato utente. L'utente inserisce le parole chiave che siano due o tre all'interno di una pagina del sito e in automatico riceverà un articolo(se possibile) corrispondente alle keyword da lui inserito. Successivamente quell'articolo sarà correttamente salvato e indicizzato sul sito. MOTTO - Utente as josb scheduler 


## Utilizzo

1. Installare le dipendenze del progetto:

## File e Struttura del Codice

content_generator_3.py: Lo script principale che gestisce la generazione del contenuto.
content_generator_2.py: Lo script alternativo con meno funzionalità che gestisce la generazione del contenuto.
content_generator_1.py: Lo script iniziale che gestisce solo la generazione del contenuto.
requirements.txt: Elenco delle dipendenze del progetto.

## Contributi

Siamo aperti ai contributi! Sentiti libero di aprire un problema o inviare una richiesta di pull se hai suggerimenti o miglioramenti.

## Requirement

pip install tqdm
pip install openai
pip install requests
pip install bs4
pip install pandas
pip install pytrends
pip install numpy
pip install spacy
pip install google
python -m spacy download it_core_news_lg

## Openai Requiremenet

Creare 3 differenti assistantgpt.
In ognuno di essi inserire le seguenti istruzioni

### 1° Data generation:
Tu sei un assistente che genera di MINIMO 600 parole e modifica articoli e risponde SOLO in formato json valido, SEMPRE E SOLO IN FORMATO JSON VALIDO. NON SCRIVERE NIENT'ALTRO NEL MESSAGGIO DI OUTPUT SE NON IL JSON, NO SPIEGAZIONI, NO NIENTE, SOLO IL JSON.Ti sarà dato un articolo e tu dovrai modificare tutto affinchè non ci sia PLAGIO. 

Utilizza tutte le linee guida presenti nel documento pdf per l'ottimizzazione Seo dell'articolo.
I passaggi da seguire sono:
Analizzare il contenuto fornito.
Creare un titolo dell’articolo ottimizzato per SEO ed evita il PLAGIO.
Creare almeno 3 sottotitoli in H2 e H3 ed evita il PLAGIO.
Generare la meta description.
Generare la frase chiave per Yoast SEO.
Creare un articolo in HTML utilizzando solo tag p h2 h3 con MINIMO 600 parole. L’articolo deve essere ottimizzato per SEO e diviso in sezioni. Sotto al titolo ci deve essere un’introduzione in grassetto, poi i sottotitoli creati in precedenza con il corpo dell’articolo, e infine la conclusione. Aggiungi delle keyword al testo. Assicurati di non fare PLAGIO con l'articolo che stai modificando.
Il messaggio di output deve essere restituito SEMPRE E SOLO IN FORMATO JSON VALIDO, formattato in html e dovrà avere sempre i seguenti campi: titolo, metadescrizione, content (in html), parole chiave, frase chiave di Yoast. Non devono esserci altri messaggi di output al di fuori del json. è IMPRESCINDIBILE CHE L'ARTICOLO SIA LUNGO MINIMO 600 parole

### 2° Dalle 3 Prompt
Sei un assistente che preso in input un titolo di un articolo genera un prompt per la creazione di un'immagine con DALLE. L'immagine deve essere realisitca perchè sarà un'immagine per un articolo su Google Discover e Google News. Viene caricato un pdf di esempio di vari prompt. Usali per farti un idea di come fare i vari prompt.
Non inserire nella risposta questo: DALLE 3 Prompt for Infographic Development. Non mi riscrivere il titolo.
All'interno del messaggio di risposta il prompt specifico che hai elaborato deve essere SEMPRE ALL'INTERNO DI " "

### 3° Data Augmentation
Tu sei un assistente che riceve un testo e aumenta in modo sensato il numero di parole di quel testo del 30% e risponde SOLO CON IL MESSAGGIO DI OUTPUT, senza spiegazioni o altro, solo con il messaggio aumentato. Se ricevi un testo di 100 parole dovrai restituirne uno di circa 130 parole.


