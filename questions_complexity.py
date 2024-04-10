import json
import os 
import textstat

directory = "questions/sociologie"
output_file = "sociologie.json"


with open(os.path.join(directory, output_file), 'r', encoding='utf-8') as file:
        data = json.load(file)

# Fonction pour calculer la complexité basée sur l'indice de lisibilité de la question
def calculer_complexite(question):
    # Calculer l'indice de lisibilité de la question
    indice_lisibilite = textstat.flesch_reading_ease(question['question'])

    # Plus l'indice de lisibilité est bas, plus la question est complexe
    # On inverse donc l'indice pour avoir une échelle où une valeur plus élevée signifie une question plus complexe
    complexite = 100 - indice_lisibilite

    return complexite

# Liste pour stocker la complexité de chaque question
complexites_questions = []

# Calculer la complexité de chaque question
for question in data['questions']:
    complexite = calculer_complexite(question)
    complexites_questions.append((question['question'], complexite))

# Trier les questions par complexité
complexites_questions = sorted(complexites_questions, key=lambda x: x[1], reverse=True)

# Afficher les questions classées par complexité
for question, complexite in complexites_questions:
    print(f"Question: {question}")
    print(f"Complexité: {complexite}")
    print()