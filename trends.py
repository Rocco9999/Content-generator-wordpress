import pandas as pd

from pytrends.request import TrendReq

import matplotlib.pyplot as plt

# Inizializza l'oggetto TrendReq
trends = TrendReq(hl='it-IT', tz=360)

# Esegui la query per ottenere le keyword suggerite
keyword_suggestions = trends.suggestions(keyword="Alexa con l’IA potrebbe essere a pagamento. Il suo nome? Alexa Plus")

# Crea un DataFrame pandas con i risultati
data_suggestions = pd.DataFrame(keyword_suggestions)

# Stampare le prime righe del DataFrame
#print(data_suggestions.head())

def analize_keyword(main_keywords):
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
    keyword_counts = {keyword: all_suggested_keywords.count(keyword) for keyword in set(all_suggested_keywords)}

    # Ordina le keyword in base al numero di occorrenze in modo decrescente
    sorted_keywords = sorted(keyword_counts, key=keyword_counts.get, reverse=True)

    # Prendi le prime 5 keyword
    top_keywords = sorted_keywords[:5]

    # Stampa le 5 migliori keyword
    print("Top 5 Keywords:", top_keywords)


main_keywords = ["Intelligenza artificiale", "ChatGpt", "Google"]
analize_keyword(main_keywords)