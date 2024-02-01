import re
from bs4 import BeautifulSoup
import spacy
from spacy.tokens import Doc, Span


# Esempio di utilizzo
test_text = "<h2>Analisi del mercato del lavoro 2024</h2><p>L’osservatorio di analisi di PageGroup ha condotto un'approfondita indagine, esaminando accuratamente più di 500 profili professionali distribuiti in 16 diversi settori di attività economica, al fine di identificare con precisione quali sono le figure professionali più richieste dal mercato del lavoro. Lo studio ha inoltre indagato in quali specifici ambiti si registra una maggiore domanda e ha fornito dati dettagliati relativi al livello di retribuzione che si può aspettare di guadagnare in queste posizioni di lavoro. Questa analisi fornisce un quadro chiaro del panorama lavorativo attuale e può essere di grande aiuto sia per chi cerca impiego sia per i datori di lavoro che cercano di comprendere meglio le tendenze del mercato per attrarre i talenti più idonei.</p><h3>Information Technology: la carenza di figure qualificate</h3><p>La maggior parte delle richieste di personale specializzato arriva dal settore dell'Information Technology, che soffre acutamente la carenza di figure altamente qualificate a fronte di una crescente necessità, causata dall’accelerazione del processo di trasformazione digitale che è stato messo in atto da molte aziende in vari settori. Attualmente, numerose imprese dedicano una grande attenzione e risorse lavorando intensamente sugli stessi temi critici, come per esempio la gestione di sistemi SAP, lo sviluppo e gestione di infrastrutture Cloud e l'ampliamento della cybersecurity. Ciò inevitabilmente crea una forte e competitiva tensione su un mercato dell'occupazione IT in cui i candidati esperti e competenti sono già estremamente difficili da reperire, a causa della loro limitata disponibilità e della forte domanda di competenze tecniche specializzate.</p><h3>Profili più ricercati e relative retribuzioni</h3><p>Tra i professionisti del settore tecnologico attualmente più ricercati si annovera la figura del security engineer. Questo esperto nel campo della sicurezza informatica può aspettarsi una retribuzione iniziale che oscilla generalmente intorno ai 50.000 euro lordi all'anno, se possiede un'esperienza lavorativa inferiore ai 5 anni. Con tempo e competenze acquisite, un security engineer esperto, vantando tra i 5 e i 10 anni di esperienza, può vedere il proprio stipendio annuale posizionarsi in una fascia che va dai 60.000 ai 70.000 euro lordi. Allo stesso modo, anche i software developer sono figure professionali estremamente richieste nel mondo del lavoro. La loro mansione primaria si focalizza sulla progettazione accurata, la creazione efficiente e la manutenzione costante dei software. Per quanto riguarda la retribuzione, un software developer che si colloca nella fascia junior può aspettarsi un salario annuo che varia mediamente tra i 30.000 e i 50.000 euro lordi, a seconda delle competenze specifiche, dell'azienda di appartenenza e del contesto di mercato in cui si inserisce.</p><p>Cambiando settore ed entrando nell’Engineering &amp; manufacturing, cresce la domanda di tecnici di manutenzione. In questo ruolo, un professionista a inizio carriera può aspirare a uno stipendio compreso tra 35.000 e 43.000 euro lordi l’anno. Con 5-10 anni di esperienza, le retribuzioni superano i 50.000 euro lordi l’anno per attestarsi a oltre 80.000 euro lordi quando si raggiunge la posizione di responsabile manutentore.</p><p>I direttori tecnici/operativi possono ambire a stipendi compresi tra 80.000 euro e 90.000 euro lordi l’anno e superano i 110.000 euro dopo almeno 10 anni di carriera. Nel settore finance &amp; account, tra i ruoli più dinamici c’è il Chief Financial Officer, con una paga tra i 90.000 e i 100.000 euro lordi l’anno per chi ha meno di 5 anni d’esperienza e che supera i 150.000 euro lordi l’anno con oltre 10 anni d’attività nel ruolo. Ottima è anche la possibilità per i credit manager, che vengono retribuiti con 45-50.000 euro lordi all’anno già nel ruolo junior, a cui si aggiunge un bonus pari in media al 10% della retribuzione.</p><h2>Torna il Btp Valore, nuova emissione dal 26 febbraio e dura 6 anni</h2><p>Nel 2023 i pagamenti digitali crescono in tutto lo Stivale del 35,5%, mentre lo scontrino medio...</p><h2>Crisi del Mar Rosso, quanto costa all'Italia</h2><p>L’esecutivo dovrebbe decidere per una stretta a breve, anche se al momento la misura non è ancora...</p><h2>Giorno Memoria, cortei pro-Palestina: tensione a Milano</h2><p>Sempre più discendenti stanno scegliendo di scolpire sul proprio corpo i numeri di serie che i...</p><h2>Usa, Washington Post: 'Trump prepara guerra commerciale contro Cina'</h2>"


nlp = spacy.load("it_core_news_lg")

def extract_keywords(text):
    doc = nlp(text)
    keywords = [ent.text for ent in doc.ents]
    return keywords

keywords = extract_keywords(test_text)
print("Parole chiave:", keywords)



# Carica il modello
nlp = spacy.load("it_core_news_lg")

def analyze_text_with_spacy(text):
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
        print(f'\nEccola{keyword}\n')
        text = pattern.sub(f'<strong>{keyword}</strong>', text, 1)


    # Aggiungi il tag <strong> intorno ai numeri
    text = re.sub(r'(\b\d+\b)', r'<strong>\1</strong>', text)

        
    return text


doc_spacy = analyze_text_with_spacy(test_text)
print("Testo con parole chiave in grassetto per HTML:")
print(doc_spacy)
