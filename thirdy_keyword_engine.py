from collections import Counter

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

# Esempio di utilizzo
spacy_keywords = ["intelligenza", "artificiale", "apprendimento", "automatico"]
trends_keywords = ["machine learning", "algoritmi", "intelligenza artificiale"]
chatgpt_keywords = ["intelligenza", "apprendimento", "tecnologia"]

migliori_keyword = valutazione_keyword(spacy_keywords, trends_keywords, chatgpt_keywords)

print("Le migliori keyword sono:")
print(migliori_keyword)
