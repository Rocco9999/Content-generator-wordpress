from urllib.parse import urlparse, urlsplit, urlunparse, urlunsplit
from GoogleNews import GoogleNews
from datetime import datetime

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



# Esempio di utilizzo
keywords_to_search = ["intelligenza artificiale", "machine learning"]

top_links = select_top_links(keywords_to_search, num_links=2)

print("I due migliori link per l'articolo sono:")
for link in top_links:
    print(link['url'])

