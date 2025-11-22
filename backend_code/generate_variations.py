import requests
import os
import Simple_Chatbot
import pandas as pd
import csv
import IonosAccess as I

def generate_paraphrases(type, Ionos):

    dict = { "synonym" : "Du formulierst eine gegebene Frage in mehrere alternative Fassungen um. Behalte die ursprüngliche Bedeutung bei, ändere jedoch Struktur, Formulierung und Tonfall. Die Antworten sollen klar verständliche Fragen sein, jeweils unterschiedlich gestaltet. Antworte ausschließlich mit den umformulierten Fragen, ohne Einleitung und ohne Kommentare.",
            "scenario" :"Du verwandelst eine kurze Frage in eine ausführliche, kontextreiche Formulierung. Füge plausible Hintergrundinformationen, situative Details und erklärende Elemente hinzu, ohne die ursprüngliche Intention zu verändern. Die Frage soll am Ende klar gestellt werden, aber in einen längeren, natürlichen Kontext eingebettet sein. Antworte ausschließlich mit der erweiterten Version, ohne Einleitung und ohne Kommentare.",
            "fehler" : "Du schreibst die gegebene Frage mit verschiedenen Tippfehlern, orthografischen Fehlern und grammatikalischen Unsauberkeiten neu. Die Bedeutung bleibt erkennbar, aber der Text wirkt fehlerhaft und unkorrekt. Antworte ausschließlich mit diesen fehlerhaften Varianten, ohne Einleitung und ohne Kommentare.",
            "keinFrage" : "Du wandelst eine gegebene Frage in verschiedene implizite Formulierungen um, bei denen das Anliegen nur angedeutet wird. Verwende keine Fragen, sondern kurze, natürliche Sätze, die den Bedarf, das Problem oder die Situation der Nutzer beschreiben. Die Bedeutung bleibt erhalten. Antwort ausschließlich mit diesen Sätzen, ohne Einleitung, ohne Listenformat, ohne Kommentare."
    }

    # Initialisation
    IONOS_API_TOKEN = Simple_Chatbot.registration()   
    MODEL_NAME = Simple_Chatbot.ChooseChatBot(IONOS_API_TOKEN)

    # Get the CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(script_dir, "faqs_metro_germanclean.csv")
    df = pd.read_csv(input_csv)

    # Check data csv file
    if "article_title_translated" not in df.columns or "article_desc_text_translated" not in df.columns:
        print("ERREUR : Les colonnes 'article_title_translated' ou 'article_desc_text_translated' sont manquantes.")
        exit()

    data = []
    # Get the answer for each question
    for index, row in df.iterrows():
        question = row["article_title_translated"]
        print(f"Question {index+1}/{len(df)} : {question[:50]}...")


        answer = Ionos.generate_content("Generiert {num_variants} Varianten der folgenden Frage :\n {question}'", temperature=0.6, system_content=dict[type])
        print(answer)
        answer = answer[1:]
        data.append([row["article_title_translated"], row["article_desc_text_translated"], answer])

    # Save new CSV
    fichier_csv = os.path.join(script_dir, f"{type}_{Ionos.model.replace("/", "_")}.csv")
    with open(fichier_csv, mode='w', newline='', encoding='utf-8') as fichier:
        writer = csv.writer(fichier)
        # Écriture de l'en-tête
        writer.writerow(["FAQ questions", "FAQ answers", "modifiert question", "type change"])

        for element in data:
            question, reponse, questions_modifiees = element
            for qm in questions_modifiees:
                writer.writerow([question, reponse, qm, type])
    
if __name__ == "__main__":
    Ionos = IonosAccess = I.IonosAccess(number=1)
    generate_paraphrases("fehler", Ionos)