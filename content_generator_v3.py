from collections import Counter
import os
import random
import re
import time
from urllib.parse import parse_qs, urlparse, urlunparse
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from tqdm import tqdm
import json
from openai import OpenAI
import requests
import base64
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
from pytrends.request import TrendReq
import numpy as np
import spacy
from spacy.tokens import Doc, Span
from GoogleNews import GoogleNews


def remove_query_params(url):
    parsed_url = urlparse(url)
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    if '&ved' in cleaned_url:
        cleaned_url = cleaned_url.split('&ved')[0]
    return cleaned_url

def get_news_links_with_keywords(keywords):
    try:
        googlenews = GoogleNews(lang='it')
        # Unisce le keyword in una stringa separata da virgola per eseguire una ricerca su più termini
        keywords_str = ', '.join(keywords)
        googlenews.search(keywords_str)

        # Ottieni i risultati delle news
        results = googlenews.result()

        # Estrai i link alle notizie con informazioni aggiuntive
        news_links = [
            {
                'title': result['title'],
                'content': result['desc'],
                'published_date': result['date'],
                'url': remove_query_params(result['link'])
            }
            for result in results
        ]

        return news_links
    except Exception as e:
        print("Errore durante la ricerca su Google News:", str(e))
        return None

def relevancy_score(link, keywords):
    # Controllo se almeno una delle parole chiave appare nel titolo o nel corpo dell'articolo
    for keyword in keywords:
        if keyword.lower() in link['title'].lower() or keyword.lower() in link['content'].lower():
            return 1  # Assegno il massimo punteggio se almeno una delle parole chiave è rilevante

    return 0  # Altrimenti, punteggio basso


def publication_date(link):
    # Ottengo la data di pubblicazione dal link (questo è un esempio, la tua implementazione può variare)
    date_str = link['published_date']
    
    try:
        # Converto la stringa della data in un oggetto datetime
        date_object = datetime.strptime(date_str, "%Y-%m-%d")
        return date_object
    except ValueError:
        # Se c'è un problema nella conversione, restituisco la data minima
        return datetime.min

def select_top_links(keywords, num_links=2):
    news_links = get_news_links_with_keywords(keywords)
    # Ordino i link in base a criteri come autorevolezza, rilevanza e data di pubblicazione
    sorted_links = sorted(news_links, key=lambda link: (relevancy_score(link, keywords), publication_date(link)), reverse=True)

    # Seleziono i primi due link come i migliori
    top_links = sorted_links[:num_links]

    return top_links



# Funzione per ottenere il conteggio delle parole da un testo
def count_words(text):
    return len(text.split())


def data_augmentation(ASSISTANT_ID_AUGMANTED, your_json):

    # Estrai il contenuto HTML dal JSON
    html_content = your_json['content']

    # Utilizza BeautifulSoup per ottenere tutti i tag <p>
    soup = BeautifulSoup(html_content, 'html.parser')
    all_p_tags = soup.find_all('p')

    # Calcola il conteggio totale delle parole
    total_word_count = sum(count_words(tag.get_text()) for tag in all_p_tags)

    # Se il conteggio è inferiore a 500, elabora i tag <p> con ChatGPT
    if total_word_count < 500:
        new_p_tags = []

        for p_tag in all_p_tags:
            if total_word_count <= 600:
                # Invia il contenuto di ciascun tag <p> a ChatGPT per ottenere più parole
                gpt_response = run_global(ASSISTANT_ID_AUGMANTED, p_tag.get_text(), 60)
                if not gpt_response.strip():
                    print("La risposta di ChatGPT è vuota o contiene solo spazi bianchi. Mantieni il messaggio originale.")
                    new_p_tags.append('<p>' + p_tag.get_text() + '</p>')
                else:
                    new_p_tags.append('<p>' + gpt_response + '</p>')
                    total_word_count = total_word_count - count_words(p_tag.get_text()) + count_words(gpt_response)
                
                

        # Sostituisci i vecchi tag <p> con quelli ottenuti da ChatGPT
        for old_p_tag, new_p_tag in zip(all_p_tags, new_p_tags):
            old_p_tag.replace_with(BeautifulSoup(new_p_tag, 'html.parser'))

        # Ricompone l'HTML dopo le sostituzioni
        new_html_content = str(soup)

        # Aggiorna il JSON con il nuovo contenuto HTML
        your_json['content'] = new_html_content
    else:
        print("Non bisogna fare nulla")

    # Ora il tuo JSON contiene il contenuto HTML modificato
    print(your_json)
    return your_json


def cal_time(article_number):
    # Ottenere la data e ora attuale
    current_datetime = datetime.now()

    # Primo range: dal momento attuale alle 20:00 dello stesso giorno
    end_time_first_range = datetime(current_datetime.year, current_datetime.month, current_datetime.day, 20, 0)
    
    # Secondo range: dal giorno successivo alle 06:00 alle 20:00 dello stesso giorno
    next_day = current_datetime + timedelta(days=1)
    start_time_second_range = datetime(next_day.year, next_day.month, next_day.day, 6, 0)
    end_time_second_range = datetime(next_day.year, next_day.month, next_day.day, 20, 0)
    second_range = [start_time_second_range + timedelta(minutes=random.randint(0, int((end_time_second_range - start_time_second_range).total_seconds() / 60))) for _ in range(article_number)]

    if end_time_first_range < current_datetime:
        selected_dates = second_range
    else:
        first_range = [current_datetime + timedelta(minutes=random.randint(0, int((end_time_first_range - current_datetime).total_seconds() / 60))) for _ in range(article_number)]
        combined_range = first_range + second_range
        selected_dates = random.sample(combined_range, article_number)

    

    # Formattazione nel formato desiderato
    selected_dates_formatted = [date.strftime('%Y-%m-%dT%H:%M:%S') for date in selected_dates]


    # Stampa
    print("Primo range:", selected_dates_formatted)

    return selected_dates_formatted


    
# Funzione per ottenere il contenuto dell'articolo
def get_article_content(url):
    try:
        # Send an HTTP GET request to the website
        response = requests.get(url)

        # Parse the HTML code using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the relevant information from the HTML code
        keywords_to_exclude = ["cookie settings", "accetta i cookie", "white paper", "informativa sulla privacy", "condizioni d'uso",
                       "ads", "pubblicità", "banner", "commenti", "seguici su", "follow us on", "ISSN", 
                       "risorse correlate", "leggi anche", "altro da questo autore", "articoli correlati",
                       "tag", "categorie", "condividi questo articolo", "leggi anche", "la tua opinione", "widget", "valuta la qualità di questo articolo", 
                       "copyright", "crediti", "client", "contenuto pubblicitario", "cookie", "@", "©", "p. iva"
                       "most popular", "nuovaparola1", "nuovaparola2", "altraparoladaevitare", "link rss",
                       "newsletter", "rispondi", "scarica", "scopri di più", "registrati", "accesso", "gratis", "prova gratuita",
                       "offerta", "promozione", "esclusivo", "limited time", "last chance", "best price", "save", "easy", "simple", "new",
                       "in arrivo", "trending", "hot", "don't delete", "unsubscribe", "purchase", "buy now", "order now", "telefono:", "p.iva", "leggi tutti"]

        content = ""
        h1_found = False
        h1_count = 0
        h2_count = 0
        h3_count = 0
        p_count = 0
        last_tag = None  # Aggiunto per tenere traccia dell'ultimo tag elaborato

        for tag in soup.find_all(['p', 'h1', 'h2', 'h3']):
            text = tag.get_text(strip=True)

            # Se ci sono due tag consecutivi dello stesso tipo, cancella il precedente
            if last_tag == tag.name and tag.name != 'p':
                content = content.rsplit(tag.name + " : " + text + '\n', 1)[0]
            

            if tag.name == 'h1':
                h1_found = True
                content += tag.name + " : " + text + '\n'
                h1_count += 1
                last_tag = 'h1'
            elif h1_found:
                if tag.name == 'h3' and h3_count < 2 and not any(keyword in text.lower() for keyword in keywords_to_exclude) and len(text.split()) >= 5:
                    if last_tag != 'h3':  # Controllo se l'ultimo tag elaborato è diverso da 'h3'
                        content += tag.name + " : " + text + '\n'
                        h3_count += 1
                        last_tag = 'h3'
                elif tag.name == 'h2' and h2_count < 4 and not any(keyword in text.lower() for keyword in keywords_to_exclude) and len(text.split()) >= 5:
                    if last_tag != 'h2':  # Controllo se l'ultimo tag elaborato è diverso da 'h2'
                        content += tag.name + " : " + text + '\n'
                        h2_count += 1
                        last_tag = 'h2'
                elif tag.name == 'p' and not any(keyword in text.lower() for keyword in keywords_to_exclude) and text.strip() and len(text.split()) >= 15:  # Cambia 5 con il numero minimo di parole desiderato
                    content += tag.name + " : " + text + '\n'
                    p_count += 1
                    last_tag = 'p'


        time.sleep(1)

        for keyword in keywords_to_exclude:

            # Converti sia la parola chiave che la stringa content in minuscolo
            keyword_lower = keyword.lower()
            content_lower = content.lower()

            # Effettua il confronto senza distinzione tra maiuscolo e minuscolo
            if keyword_lower in content_lower:
                content = content.split(keyword, 1)[0]

        # Se non ci sono tag p nel contenuto finale, restituisci None
        if p_count < 5 or h1_count > 1:
            print("Nessun tag p trovato. Escludi il contenuto.")
            return False, None
        else:
            print(content)
            return True, content

    except Exception as e:
        print("Errore durante l'accesso")
        return False, None


def save_url(xml_url):
    # Creare un dizionario con il contenuto degli articoli
    content_dict = {}
    count = 0

    if "alerts/feeds/" in xml_url:
        # Scarica il contenuto del file XML
        with urlopen(xml_url) as response:
            xml_content = response.read()

        # Analizza il file XML
        tree = ET.fromstring(xml_content)

        # Estrai i dati XML e crea una lista di dizionari
        data_list = []
        for entry in tree.findall('.//{http://www.w3.org/2005/Atom}entry'):
            entry_data = {}
            entry_data = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
            # Parsing dell'URL completo
            parsed_url = urlparse(entry_data)

            # Estrazione dell'URL desiderato dalla query string
            desired_url = parse_qs(parsed_url.query).get('url', [''])[0]
            if "youtube" not in desired_url:
                data_list.append(desired_url)


        # Itera attraverso i link e aggiorna il contenuto
        for entry_data in tqdm(data_list, desc="Elaborazione articoli"):
            url = entry_data
            esit, content = get_article_content(url)
            if esit is True:
                content_dict[count] = content
                count += 1
    
    else:
        esit, content = get_article_content(xml_url)
        if esit is True:
            content_dict[count] = content
            count += 1
        
    return content_dict, count

def run_global(ASSISTANT_ID, message, max_wait_time):
    # Make sure your API key is set as an environment variable.
  client = OpenAI()

  # Create a thread with a message.
  thread = client.beta.threads.create(
      messages=[
          {
              "role": "user",
              # Update this with the query you want to use.
              "content": str(message),
          }
      ]
  )

  # Submit the thread to the assistant (as a new run).
# Submit the thread to the assistant (as a new run).
  run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
  print(f"👉 Run Created: {run.id}")

  # Set the maximum wait time
  start_time = time.time()

  # Wait for run to complete.
  while run.status != "completed":
    # Check for timeout
    if time.time() - start_time > max_wait_time:
        print("⚠️ Maximum wait time reached. Exiting.")
        break

    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    print(f"🏃 Run Status: {run.status}")
    time.sleep(1)

  else:
    print(f"🏁 Run Completed!")

  # Get the latest message from the thread.
  message_response = client.beta.threads.messages.list(thread_id=thread.id)
  messages = message_response.data

  # Print the latest message.
  latest_message = messages[0]

  openai_response_message = latest_message.content[0].text.value
  

  return openai_response_message

def run_message_augmentation(ASSISTANT_ID, message):
  
  data = run_global(ASSISTANT_ID, message, 50)

  # Se la risposta è vuota o contiene solo spazi bianchi, mantieni il messaggio originale
  if not data.strip():
    print("La risposta di ChatGPT è vuota o contiene solo spazi bianchi. Mantieni il messaggio originale.")
    data = str(message)

  return data

def convert_json(openai_response_message, old_message):
    try:
        # Prova a caricare come JSON
        converted_message = json.loads(openai_response_message)

        # Se il caricamento ha successo, lavora con data_json
        print("Caricato come JSON:", converted_message)
        # ... (fai quello che devi fare con data_json)

    except json.JSONDecodeError:
        try:
            new_openai_response_message = run_global(ASSISTANT_ID, old_message, 60)
            converted_message = json.load(new_openai_response_message)

        except:
            # Se si verifica un errore durante il caricamento come JSON, trattalo come testo normale e convertilo in JSON
            print("Non è un JSON valido, convertito in JSON:", openai_response_message)
            converted_message = {"text_as_json": openai_response_message}

    # Utilizza BeautifulSoup per ottenere tutti i tag <p>
    soup = BeautifulSoup(converted_message['content'], 'html.parser')
    all_p_tags = soup.find_all('p')

    # Calcola il conteggio totale delle parole
    total_word_count = sum(count_words(tag.get_text()) for tag in all_p_tags)

    return converted_message, total_word_count


def push_post1(article, media_url, green_pass, date, nlp, author, category):
    url = 'https://www.your-project/wp-json/wp/v2/posts'
    user = 'push_article'
    password = 'UiQS UPuH jLYg qUl4 nc0e eFsJ'

    # Estrarre i singoli valori dall'oggetto
    titolo = article['title']
    content = article['content']
    keyword = article['keyword']
    keyphrase = article['keyphrase']
    metadescription = article['metadescription']

    content_review, spacy_keyword = analyze_text_with_spacy(content, nlp)

    # Dividi la stringa in una lista utilizzando la virgola come delimitatore
    keywords_list = [keyword.strip() for keyword in keyword.split(',')]

    keywords_analized = analyze_keyword(keywords_list[:2])
    data = ", ".join(keywords_analized)
    final_keywords = data.split(',')
    
    migliori_keyword = valutazione_keyword(keywords_analized, keywords_list, spacy_keyword)
    best_keyword = ", ".join(migliori_keyword)
    final_best_keywords = best_keyword.split(',')

    top_links = select_top_links(migliori_keyword, num_links=2)

    print("I due migliori link per l'articolo sono:")
    paragraph_link = ''
    index_count = 0
    for link in top_links:
        print(link['url'])
        paragraph_link =  paragraph_link + '\n<a href=' + link['url'] + 'data-id=' + link['url'] + '>' + link['title'] +'</a>'
        index_count += 1

    paragraph_link = '<p>' + paragraph_link + '</p>'

    post = {
        'date': date,
        'title': titolo,
        'content': (content_review + paragraph_link +' keyword: \n' + keyword + '\n best Keyword: \n' + best_keyword + '\nkeyphrase: \n' + keyphrase + '\n metadescriprion: \n ' + metadescription),
        'status': 'pending',
        'author': author,  # ID dell'autore (verifica quale ID corrisponde all'autore desiderato)
        'categories': category,
        'sticky': random.choice([True, False])
    }

    #keywords_string = keyword.split(',')

    # Se ci sono più di una parola chiave, crea una nuova stringa con le prime due separate da virgola
    if len(final_best_keywords) > 1:
        onekwyword = ", ".join(final_best_keywords[:2])
    else:
        onekwyword = final_best_keywords[0]

    # Send the HTTP request to create the post
    response = requests.post(url, auth=(user, password), json=post)

    # Check the response for post creation
    if response.status_code == 201 and media_url is not None:
        print('Post created successfully')
        raw = requests.get(media_url).content
        with NamedTemporaryFile(delete=False, mode="wb", suffix=".jpg") as img:
            img.write(raw)
            temp_image_path = img.name  # Ottenere il percorso del file temporaneo


        wp_response = wp_upload_image(user, password, temp_image_path, keyphrase, onekwyword)
        print("Response from WP: ", wp_response)

        # Estrai l'ID dell'immagine caricata
        image_id = wp_response.json().get('id')
        post_id=response.json().get('id')

        # Imposta l'immagine in evidenza per l'articolo
        if green_pass is True:
            set_featured_image(user, password, post_id, image_id)
    else:
        print('Failed to create post: ' + response.text)

    if response.status_code == 201:
        set_meta(user, password, post_id, onekwyword, metadescription)

def analyze_text_with_spacy(text, nlp):
    # Utilizza BeautifulSoup per analizzare l'HTML
    soup = BeautifulSoup(text, 'html.parser')

    # Rimuovi i tag desiderati
    for tag in ['p', 'h1', 'h2', 'h3']:
        for match in soup.find_all(tag):
            match.replace_with_children()

    # Ottieni il testo senza i tag
    text_without_tags = soup.get_text(separator=' ', strip=True)
    # Processa il testo con spaCy
    doc = nlp(text_without_tags)
    keywords_with_duplicates = [ent.text for ent in doc.ents]
    # Rimuovere i duplicati
    keywords = list(set(keywords_with_duplicates))
    # Aggiungi le keyword come entità personalizzate
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(f'<strong>{keyword}</strong>', text, 1)
    
    
    # Aggiungi il tag <strong> intorno ai numeri
    text = re.sub(r'(\b\d+\b)', r'<strong>\1</strong>', text)
    
    return text, keywords
    

def set_featured_image(user, password, post_id, image_id):
    url = f'https://www.your-project/wp-json/wp/v2/posts/{post_id}'
    headers = {'Content-Type': 'application/json'}

    data = {
        'featured_media': image_id
    }

    response = requests.post(url, auth=(user, password), headers=headers, json=data)
    print("Set featured image response: ", response.text)


def wp_upload_image(user, password, img_path, keyphrase, onekwyword):
    url = 'https://www.your-project/wp-json/wp/v2/media'
    headers = {'Content-Disposition': 'attachment; filename=%s' % "image.jpg"}
    time = (datetime.now()).strftime("%d-%m-%Y")
    onekwyword = onekwyword + "-"+time + ".jpeg"
    try:
        with open(img_path, 'rb') as fp:
            files = {
                'file': (onekwyword, fp, 'image/jpeg'),
            }

            # Aggiungi altri campi desiderati
            data = {
                'description': keyphrase
            }
            rs = requests.post(url, auth=(user, password), headers=headers, files=files, data=data)
            return rs
    except IOError as e:
        print(f"Couldn't open file ({e})")

def set_meta(user, password, post_id, onekwyword, metadescription):
    url = f'https://www.your-project/wp-json/rankmath/v1/updateMeta'
    object_type = 'post'  # Può variare a seconda dell'oggetto a cui vuoi aggiungere la metadescrizione
    meta = {'rank_math_description': metadescription, 'rank_math_focus_keyword': onekwyword}  # Sostituisci con la tua metadescrizione

    params = {
        'objectType': object_type,
        'objectID': post_id,
        'meta': meta
    }

    # Effettua la richiesta POST
    response = requests.post(url, auth=(user, password), json=params)
    print("Set fmetadescription: ", response.text)


client = OpenAI()

def get_image_from_DALL_E_3_API(user_prompt,
                               image_dimension="1024x1024",
                               image_quality="standard",
                               model="dall-e-3",
                               nb_final_image=1):
   
    try:
        response = client.images.generate(
            model = model,
            prompt = user_prompt,
            size = image_dimension,
            quality = image_quality,
            n=nb_final_image,
        )
        image_url = response.data[0].url
    except:
       image_url = None

    return image_url

def restruct_object(article):
    # Supponendo che 'article' sia il tuo oggetto convertito dal JSON
    article_keys = list(article.keys())

    # Gestione del caso in cui non verrà restituito un json
    if 'text_as_json' in article:
        labeled_article = {
           #nel qui abbiamo tutti i numeri uguali ma in content abbiamo article_key 0
            'title':'Articolo con problemi',
            'metadescription':'non esiste',
            'content': article.get(article_keys[0], 'non esiste'),
            'keyword': 'non esiste',
            'keyphrase': 'non esiste'
    } 
    else:
        labeled_article = {
            'title': article.get(article_keys[0], 'non esiste'),
            'metadescription': article.get(article_keys[1], 'non esiste'),
            'content': article.get(article_keys[2], 'non esiste'),
            'keyword': article.get(article_keys[3], 'non esiste'),
            'keyphrase': article.get(article_keys[4], 'non esiste')
        }

    # Ora puoi utilizzare l'oggetto labeled_article come desiderato
    return labeled_article

def run_message_prompt(ASSISTANT_ID, message):

    data = run_global(ASSISTANT_ID, message, 50)

    print(data)
    
    final_prompt = data.split('"')
    if (len(final_prompt)) >= 7:
            prompt = message
    elif(len(final_prompt)) >= 4:
            prompt = str(final_prompt[3])
    else:
            prompt = str(final_prompt[1])
        
    return prompt



def analyze_keyword(main_keywords):
    # Inizializza l'oggetto TrendReq
    trends = TrendReq(hl='it-IT', tz=360)

    # Dizionario per memorizzare le keyword suggerite per ciascuna delle 10 keyword principali
    suggested_keywords_dict = {}

    # Itera attraverso le 10 keyword principali
    for keyword in main_keywords:
        # Esegui la query per ottenere le keyword suggerite
        keyword_suggestions = trends.suggestions(keyword=keyword)
        
        # Estrai le 5 keyword suggerite più forti
        top_suggestions = keyword_suggestions[:5]
        
        # Aggiungi le keyword suggerite al dizionario
        suggested_keywords_dict[keyword] = [entry['title'] for entry in top_suggestions]

    # Flatten della lista di keyword suggerite
    all_suggested_keywords = [keyword for keywords_list in suggested_keywords_dict.values() for keyword in keywords_list]

    # Conta le occorrenze di ciascuna keyword
    keyword_counts = Counter(all_suggested_keywords)

    # Trova le migliori 5 keyword
    top_keywords_with_counts = keyword_counts.most_common(5)
    top_keywords = [keyword for keyword, count in top_keywords_with_counts]

    # Stampa le 5 migliori keyword con i relativi conteggi
    print("Top 5 Keywords:")
    for keyword, count in top_keywords_with_counts:
        print(f"{keyword}: {count} occorrenze")
    
    return top_keywords

def valutazione_keyword(spacy_keywords, trends_keywords, chatgpt_keywords):
    # Converti tutte le keyword in lettere minuscole
    spacy_keywords = [kw.lower() for kw in spacy_keywords]
    trends_keywords = [kw.lower() for kw in trends_keywords]
    chatgpt_keywords = [kw.lower() for kw in chatgpt_keywords]

    # Considera la rilevanza al contesto
    spacy_relevanza = Counter(spacy_keywords)
    trends_relevanza = Counter(trends_keywords)
    chatgpt_relevanza = Counter(chatgpt_keywords)

    # Combina i conteggi di rilevanza
    conteggi_combinati = spacy_relevanza + trends_relevanza + chatgpt_relevanza

    # Ordina le keyword in base ai punteggi
    keyword_ordine = sorted(conteggi_combinati, key=lambda x: conteggi_combinati[x], reverse=True)

    # Seleziona le prime 5 keyword come le migliori
    migliori_keyword = keyword_ordine[:5]

    return migliori_keyword

# URL del file XML
#Carico modello per estrazione keyword dal testo
nlp = spacy.load("it_core_news_lg")
ASSISTANT_ID = "asst_xxx"
DALLE3_PROMPT_ASSISTANTID = "asst_xxx"
ASSISTANT_ID_AUGMANTED = "asst_xxx"
#Sezione url. Commentare per cambiare tipo, possibile inserire sia url xml di google, sia url normali di articoli
xml_url = ""
single_url = ""
xml_url_smartphone= ""


#Estrazione contenuti degli articoli
content_url, article_number= save_url(single_url)
#Creazione date random per articoli
date_random = cal_time(article_number)

print(article_number)
#Contatore per inserimento data in articolo
count = 0

#1 Ignazio Ferri, IA
#3 Giogio Andreas
#4 Federico Berni
#5 Giuliana Cavalieri
AUTHOR = 3

#4 IA
#113 Smartphone 
#132 Lavoro ai
#110 Coding
#111 Space
#9
CATEGORY = [4]

# Funzione per eseguire il ciclo
def process_key_value(key, value, ASSISTANT_ID, image_url, date, nlp):
    try:
        openai_response = run_global(ASSISTANT_ID, value, 60)
        converted_message, total_word_count = convert_json(openai_response, value)
        if total_word_count > 250:
            if 'text_as_json' not in converted_message:
                openai_response_augmentated = data_augmentation(ASSISTANT_ID_AUGMANTED, converted_message)
                labeled_article = restruct_object(openai_response_augmentated)
            else:    
                labeled_article = restruct_object(converted_message)
            #Variabile sblocco funzione per generazione immagine
            green_pass = None
            if (image_url is None) and ('text_as_json' not in converted_message): #test_as_json identifica un messaggio non correttamente formattato, pertanto verrà escluso
                data=run_message_prompt(DALLE3_PROMPT_ASSISTANTID, labeled_article['title'])
                image_url = get_image_from_DALL_E_3_API(data)
                green_pass = True
                push_post1(labeled_article, image_url, green_pass, date, nlp, AUTHOR, CATEGORY)
            
        return True, image_url  # Successo

    except Exception as e:
        print(f"Errore durante l'elaborazione di key={key} (retry): {e}")
        return False, image_url  # Errore
    

# Uso della funzione
for key, value in list(content_url.items()):
#for key, value in (list(content_url.items()))[:4]:
    attempts = 2  # Numero massimo di tentativi
    image = None
    for _ in range(attempts):
        success, image = process_key_value(key, value, ASSISTANT_ID, image, date_random[count], nlp)

        if success:
            break
        else: 
           print(f"Tentativo fallito per key={key}. Ritentando...")

    count +=1
