# Application web pédagogique sur un quiz interactif aux participants
Dans ce projet, j'ai mis en place une application web pour mon association Préserve ton Droit en utilisant le Framework Flask. <br>
L'objectif de cette application de répondre aux différents questions sur 4 catégories (Droit,Humanitaire, Culturel,Sociologie ) pour permettre aux participants d'apprendre et de découvrir la vision juridique,humanitaire, culturel et social.  <br>
Cette application sera stockée dans les différents bases de données aux comptes d'utilisateurs ainsi que les résultats aux réponses des quiz. <br> 

## Description de l'application 
- app.py # Application principale 
- models.py # Modélisation des données 
- mail.py #Procédure de confirmation de mail
- vizualisation.py #Visualisations des résultats sur les catégories
- template/ # Liste des pages 
- static/images # Liste des images
- static/styles # Fichiers CSS
- questions/ # Fichiers JSON contenant une série de questions

## Formulaire pour la participation du concours du quiz

- nom 
- prenom 
- adresse 
- code_postal
- ville 
- niveau_etude 
- statut 
- centre_interet 
- choix_categorie 

## Base de données    
- participants.db # On dispose 3 tables:
    - User : Nombre de participants ayant inscrit l'application du quiz
    - participant : Le nombre de participants ayant rempli le formulaire
    - reponse_participant : Le nombre de réponses effectués par un participant

## Installation
- Version Python 3.11.7 

Importer le lien du projet et puis créez votre environnement virtuel
```
$ git clone https://github.com/vincent-tran-94/Quiz_students_PTD_application.git
$ python3 -m venv venv
$ . venv/bin/activate
```

Installer les dépendances 
```
$ (venv) pip install -r requirements.txt 
```

Lancer votre application Flask 
```
$ (venv) python main.py
```
