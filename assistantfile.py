import time
import requests
from bs4 import BeautifulSoup
from openai import ChatCompletion, OpenAI  # Assicurati di installare il pacchetto 'openai'

# Funzione per ottenere il conteggio delle parole da un testo
def count_words(text):
    return len(text.split())

def run_message(ASSISTANT_ID, message):
  
  print("Inizio data augmentation")

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
  run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
  print(f"👉 Run Created: {run.id}")

  # Wait for run to complete.
  while run.status != "completed":
      run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
  else:
      print(f"🏁 Run Completed!")

  # Get the latest message from the thread.
  message_response = client.beta.threads.messages.list(thread_id=thread.id)
  messages = message_response.data

  # Print the latest message.
  latest_message = messages[0]

  data = latest_message.content[0].text.value

  # Se la risposta è vuota o contiene solo spazi bianchi, mantieni il messaggio originale
  if not data.strip():
    print("La risposta di ChatGPT è vuota o contiene solo spazi bianchi. Mantieni il messaggio originale.")
    data = str(message)

  return data


# Esempio di JSON
your_json = {'titolo': 'The Impact of Artificial Intelligence on Society: Reflections by Father Pasqualetti', 
             'metadescrizione': "Read about the impact of artificial intelligence on society and the reflections of Father Pasqualetti, Dean of the School of Social Communications at the Pontifical Salesian University, on Pope Francis' message for the 58th World Day of Social Communications.", 
             'content': "<h2>Artificial Intelligence and Society</h2><p>The use of artificial intelligence is inevitable. Our societies will be increasingly integrated by AI systems. But what will our understanding of social relations look like? What will be the meaning of freedom and democracy? These are some of the questions reflected upon by Fr. Fabio Pasqualetti, Dean of the School of Social Communications at the Pontifical Salesian University and Advisor to the Dicastery for Communications. He considered Pope Francis’ message for the 58th World Day of Social Communications, entitled “Artificial Intelligence and the Wisdom of the Heart: for a fully human communication.”</p><h2>The Wisdom of the Heart</h2><p>The Pope's message invites us to start from the “wisdom of the heart” in an age “rich in technology and poor in humanity”. It emphasizes the need to reposition ourselves in the right place, acknowledging the beauty of diversity and the interconnectedness of humanity within the cosmos. Fr. Pasqualetti lamented the current focus on conflicts based on race, nations, and borders, instead of working together for a better world.</p><h2>Transparency and Good Journalism</h2><p>Fr. Pasqualetti highlighted the need for transparency in AI systems and cultural information, drawing a parallel to the labeling of food packaging to inform consumers about the ingredients and origin. He also cautioned against disintermediation, urging for the rejection of deliberate information polluters and the promotion of good journalism to help people understand the impact of AI on society. Professional mediation, he asserted, is essential in the age of information overload.</p><h2>Ethical Regulation and International Treaty</h2><p>In line with Pope Francis' message, Fr. Pasqualetti called for the ethical regulation of AI through a “binding international treaty”. This call reinforces the importance of establishing ethical guidelines and frameworks to govern the development and use of AI, ensuring that it aligns with human values and promotes the well-being of society.</p><h2>Conclusion</h2><p>Fr. Pasqualetti's reflections offer a thought-provoking perspective on the impact of artificial intelligence on society and the imperative of integrating the “wisdom of the heart” to ensure a fully human communication amidst the technological advancements. His insights underscore the significance of transparency, ethical regulation, and the role of good journalism in navigating the evolving landscape influenced by AI.</p>", 
             'parole chiave': 'artificial intelligence, society, AI systems, transparency, good journalism, ethical regulation, international treaty', 
             'frasechiaveyoast': 'impact of artificial intelligence on society'}


def data_augmentation():

    # Estrai il contenuto HTML dal JSON
    html_content = your_json['content']

    # Utilizza BeautifulSoup per ottenere tutti i tag <p>
    soup = BeautifulSoup(html_content, 'html.parser')
    all_p_tags = soup.find_all('p')

    # Calcola il conteggio totale delle parole
    total_word_count = sum(count_words(tag.get_text()) for tag in all_p_tags)

    ASSISTANT_ID = "asst_xxx"
    # Se il conteggio è inferiore a 500, elabora i tag <p> con ChatGPT
    if total_word_count < 500:
        new_p_tags = []

        for p_tag in all_p_tags:
            # Invia il contenuto di ciascun tag <p> a ChatGPT per ottenere più parole
            gpt_response = run_message(ASSISTANT_ID, p_tag.get_text())
            new_p_tags.append(gpt_response)

        # Sostituisci i vecchi tag <p> con quelli ottenuti da ChatGPT
        for old_p_tag, new_p_tag in zip(all_p_tags, new_p_tags):
            old_p_tag.replace_with(BeautifulSoup(new_p_tag, 'html.parser'))

    # Ricompone l'HTML con i nuovi tag <p> ottenuti da ChatGPT
    new_html_content = str(soup)

    # Aggiorna il JSON con il nuovo contenuto HTML
    your_json['content'] = new_html_content

    # Ora il tuo JSON contiene il contenuto HTML modificato
    print(your_json)

