# Application web pédagogique sur un quiz interactif aux participants
Dans ce projet, j'ai mis en place une application web pour mon association Préserve ton Droit en utilisant le Framework Flask. <br>
L'objectif de cette application de répondre aux différents questions sur 4 catégories (Droit,Humanitaire, Culturel,Sociologie ) pour permettre aux participants d'apprendre et de découvrir la vision juridique,humanitaire, culturel et social.  <br>
Cette application sera stockée dans les différents bases de données aux comptes d'utilisateurs ainsi que les résultats aux réponses des quiz. <br> 

Voici la consigne de l'application:

- Fonctionnalité de login et d'inscription via par mail (on peut changer de mot de passe et supprimer de compte) 
- Formulaire de renseignements pour renseigner la personne du participant s'il gagnera le lot
- 4 catégories à choisir (droit, humanitaire, culturel, sociologie)
- On a le droit de participer une fois par catégorie une fois qu'on a soumis les réponses des questionnaires
- Chaque point de réponse (pour l'instant compte 1 point par bonne réponse) (je vais voir plus tard si c'est possible d'ajuster les points de réponses pour les nouvelles questionnaires)
- Les données des résultats seront affichés sur une page de visualisation qui contient:  <br>
&rarr; Taux de réussite en moyenne calculé pour tout les participants à chaque catégorie <br>
&rarr; Le nombre de participants répondus par catégorie  <br>
&rarr; Le nombre de participants répondus en fonction du mois pour chaque catégorie   <br>
&rarr; Le classement des 50 meilleurs participants (pour chaque mois et année) ayant répondu tout les catégories  <br>

Cette application va permet aux participants d'apprendre et de découvrir des notions sur le domaine  juridique, humanitaire, culturel et social dans notre société en général.

## Description de l'application 
- app.py # Application principale 
- models.py # Modélisation des données 
- mail.py #Procédure de confirmation de mail
- vizualisation.py #Visualisations des résultats sur les catégories
- template/ # Liste des pages 
- static/images # Liste des images
- static/videos # Liste des vidéos
- static/styles # Fichiers CSS
- static/JS #Fichiers de JavaScript 
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
    - contact: contact client des participants soumis dans l'application 

## Installation
- Version Python 3.11.7 

Importer le lien du projet et puis créez votre environnement virtuel
```
$ git clone https://github.com/vincent-tran-94/Quiz_students_PTD_application.git
$ python3 -m venv env
$ source env/Scripts/activate
```

Installer les dépendances 
```
$ (venv) pip install -r requirements.txt 
```

Lancer votre application Flask 
```
$ (venv) python main.py
```
