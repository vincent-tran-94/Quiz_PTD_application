# Application web pédagogique sur un quiz interactif aux participants
Dans ce projet, j'ai mis en place une application web pour mon association Préserve ton Droit en utilisant le Framework Flask. <br>
L'objectif de cette application de répondre aux différents questions sur 3 catégories (Droit,Humanitaire et Culturel) pour permettre aux participants d'apprendre et de découvrir le domaine juridique et humanitaire.  <br>
Cette application sera stockée dans les différents bases de données aux comptes d'utilisateurs ainsi que les résultats aux réponses des quiz. <br> 

## Description de l'application 
- app.py # Application principale 
- template/ # Liste des pages 
- static/images # Liste des images
- static/styles # Fichiers CSS
- models.py # Modélisation des données 
- mail.py #Procédure de confirmation de mail
- questions/ # Fichiers JSON contenant une série de questions


## Base de données    
- participants.db # On dispose 3 tables:
    - participant : Le nombre de participants ayant rempli le formulaire
    - reponse_participant : Le nombre de réponses effectués par un participant
    - email_id : Nombre de participants ayant reçu la confirmation par mail

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
