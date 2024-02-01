import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from tqdm import tqdm
import json
from openai import OpenAI
import requests
import base64

# Funzione per ottenere il contenuto dell'articolo
def get_article_content(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Esegui Chrome in background
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')

        chrome_driver = webdriver.Chrome(options=chrome_options)

        chrome_driver.get(url)
        WebDriverWait(chrome_driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'p')))
        time.sleep(5)

        page_source = chrome_driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        elements_to_exclude = ['cookie', 'banner', 'ads', 'img', 'comment']
        paragraphs = []
        for element in soup.find_all(['p', 'h1', 'h2']):
            if not any(div_id in [parent.get('id') for parent in element.parents] for div_id in elements_to_exclude):
                paragraphs.append(element.get_text())

        content = ' '.join(paragraphs)

        keywords_to_exclude = ["Cookie settings", "Accetta i cookie", "white paper", "Informativa sulla privacy", "Condizioni d'uso",
                               "Ads", "Pubblicità", "Banner", "Commenti", "Seguici su", "Follow us on",
                               "Risorse correlate", "Leggi anche", "Altro da questo autore", "Articoli correlati",
                               "Tag", "Categorie", "Condividi questo articolo", "Leggi anche", "La tua opinione", "widget", "Valuta la qualità di questo articolo"]

        for keyword in keywords_to_exclude:
            if keyword in content:
                content = content.split(keyword, 1)[0]

        chrome_driver.quit()

        print(content)
        return True, content

    except Exception as e:
        print("Errore durante l'accesso")
        return False, None


def run_message(ASSISTANT_ID, message):

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
  max_wait_time = 40
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

  data = latest_message.content[0].text.value
  try:
    # Prova a caricare come JSON
    data_json = json.loads(data)

    # Se il caricamento ha successo, lavora con data_json
    print("Caricato come JSON:", data_json)
    # ... (fai quello che devi fare con data_json)

  except json.JSONDecodeError:
    # Se si verifica un errore durante il caricamento come JSON, trattalo come testo normale e convertilo in JSON
    print("Non è un JSON valido, convertito in JSON:", data)
    data_json = {"text_as_json": data}

  return data_json

def push_post(article):
    
  url = 'https://www.beyond-binary-bits.cloud/wp-json/wp/v2/posts'

  user = 'push_article'
  password= 'UiQS UPuH jLYg qUl4 nc0e eFsJ'
  # Estrarre i singoli valori dall'oggetto
  titolo = article['title']
  content = article['content']
  keyword = article['keyword']
  keyphrase = article['keyphrase']
  metadescription = article['metadescription']

  post = {
      'date': '2024-01-16T12:00:00',
      'title': titolo,
      'content': (content + 'keyword' + keyword + 'keyphrase' + keyphrase + 'metadescriprio' + metadescription),
      'status': 'draft',
      'author': 1  # ID dell'autore (verifica quale ID corrisponde all'autore desiderato)
  }

  # Send the HTTP request
  response = requests.post(url, auth=(user, password), json=post)
  # Check the response
  if response.status_code == 201:
      print('Post created successfully')
  else:
      print('Failed to create post: ' + response.text)

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

# URL del file XML
url = "https://www.hwupgrade.it/news/apple/google-gemini-e-il-fulcro-dell-ia-dei-nuovi-galaxy-s24-big-g-presenta-una-valanga-di-novita_123472.html"
esit, content= get_article_content(url)
if esit is not None:
    print(content)
    ASSISTANT_ID = "asst_VSE5yMqGA1TrMq9ZTTGpnxEM"
    article = run_message(ASSISTANT_ID, content)
    labeld_article = restruct_object(article)
    push_post(labeld_article)

    #message ='<h2>DataCore Software compra WIN: lo storage entra nell’era dell’AI</h2> <p class="wp-block-d360-gutenberg-blocks-block-occhiello">acquisizioni</p> <h1 class="wp-block-post-title">DataCore Software compra WIN: lo storage entra nell’era dell’AI</h1> <p class="wp-block-post-excerpt__excerpt">Sfruttare la potenza dell’intelligenza artificiale per la gestione dell’ingente quantità di informazioni generata nei luoghi più disparati. Ecco come l’AI, frutto dell’acquisizione di Workflow Intelligence Nexus (WIN), rinnova questo settore</p> <p></p> <p><strong>DataCore Software</strong> acquisisce<strong> Workflow Intelligence Nexus (WIN)</strong> per portare <strong>l’AI</strong> nello <a href="https://www.bigdata4innovation.it/news/datacore-lancia-bolt-storage-per-le-piattaforme-devops/" rel="noopener" target="">storage</a> dei dati. Ecco come l’<strong>intelligenza artificiale</strong> rinnova questo settore.</p> <p class="ez-toc-title">Indice degli argomenti</p> <h2 class="wp-block-heading"><span class="ez-toc-section" id="DataCore_Software_compra_Workflow_Intelligence_Nexus_piu_AI_nello_storage"></span>DataCore Software compra <strong>Workflow Intelligence Nexus</strong>: più AI nello storage<span class="ez-toc-section-end"></span></h2> <p>La società ha<strong> acquisito Workflow Intelligence Nexus</strong> (WIN), un’azienda specializzata in software e servizi per la gestione dei workflow per distribuire e automatizzare i flussi di lavoro multimediali via <strong>cloud e intelligenza artificiale</strong>.</p> <p>Si tratta del <strong>primo passo per adottare l’AI nella gestione dello storage</strong>, rinnovando radicalmente il trattamento della <strong>memorizzazione</strong> dei <strong>dati</strong>, in particolare nei luoghi periferici (<strong>edge</strong>) lontani dal <strong>data center</strong>.</p> <p>“Se si guarda all’intelligenza artificiale, è da più di un decennio che è presente in varie forme: prima era chiamata<strong> machine learning</strong>”, afferma <strong>Dave Zabrowski</strong>, CEO di DataCore Software. “Ora non usiamo più quel termine, ma proprio di questo si tratta. Adesso la chiamiamo AI: suona meglio, ma è la stessa cosa. L’intelligenza artificiale è molto complicata, perché presenta molteplici sfaccettature. Certamente sta generando molta preoccupazione e confusione, ma siamo anche di fronte a enormi opportunità”.</p> <p>DataCore è<strong> nel Gartner Magic Quadrant 2023</strong> per i File System Distribuiti e l’Object Storage.</p> <h2 class="wp-block-heading"><span class="ez-toc-section" id="Gartner_i_dati_non_strutturati_triplicheranno_entro_il_2026"></span>Gartner: i dati non strutturati triplicheranno entro il 2026<span class="ez-toc-section-end"></span></h2> <p>I dati non sono più presenti nell’infrastruttura orizzontale, gestita nel core. Le aziende li raccolgono a un livello astratto più alto, un cambiamento avnenuto nell’arco degli ultimi anni. Soltanto cinque anni fa l’80% delle informazioni era composta di dati strutturati, gestiti da database o applicazioni ad hoc, oggi è l’opposto.</p> <p>Secondo la società d’analisi <strong>Gartner</strong>, <strong>entro il 2026</strong>, le grandi imprese <strong>triplicheranno</strong> rispetto all’anno scorso la quantità di dati non strutturati nelle <strong>sedi on-premise, nell’edge e nel cloud pubblico</strong>.</p> <p>Non solo le informazioni sono numerosi, ma si trovano anche in luoghi molto diversi e richiedono la trasmissione da qualche parte al fine della loro elaborazione.</p> <p>La vision DataCore.Next non è più solo estesa ai data center, perché i dati passano attraverso il cloud e l’edge, per poi tornare indietro.</p> <p>Nasce qui il bisogno di superare la classica memorizzazione ed eventuale trasporto dei dati. Infatti in futuro occorre sfruttare la potenza dell’intelligenza artificiale per la gestione dell’ingente quantità di informazioni generata nei luoghi più disparati.</p> <p>“Molti di questi dati oggi vengono prodotti e gestiti in luoghi periferici, nel cosiddetto edge. Nel modello di elaborazione tradizionale bisognava prendere quei dati e portarli all’unità di elaborazione centrale nel data center. Questi enormi set di dati richiedono un sacco di tempo per farlo, e quindi li elaboriamo localmente lavorando molto sui metadati, che sono solo una frazione dei dati totali”.</p> <h2 class="wp-block-heading"><span class="ez-toc-section" id="Lapproccio_di_DataCore_Software_allAI"></span>L’approccio di DataCore Software all’AI<span class="ez-toc-section-end"></span></h2> <p>L’approccio di DataCore Software all’AI consiste dunque in un lavoro di analisi dei dati e non solo di gestione degli spostamenti o esecuzione del backup. Funge da c<strong>onnettore che collega l’app sorgente dei dati all’infrastruttura</strong>. DataCore li prende, li inserisce nell’infrastruttura, li gestisce in modo efficiente e reinserisce i metadati nell’app che li ha generati.</p> <p>Integrando le soluzioni di Workflow Intelligence Nexus nel portfolio di soluzioni DataCore Software, si coniugano forti capacità di automazione del workflow con una robusta esperienza nella fornitura di valore.</p> <p>Inoltre WIN è attiva nel <strong>settore dei Media e dell’Entertainment</strong>, dunque la sua proposta si inserisce nella<strong> business unit Perifery</strong>, focalizzata sulla gestione dei <strong>mercati verticali</strong>.</p> <p><strong>Per l’AI nello storage il dado è tratto.</strong> “Oggi siamo presenti in tutte le aree strategiche del settore, dal core al cloud, fino all’edge,” conclude Zabrowski. “Ora è venuto il momento di mettere insieme tutti gli elementi indispensabili per creare un prodotto (…) capace di superare le criticità che vediamo nell’intelligenza artificiale”.</p> <p class="rmp-heading rmp-heading--title">'

