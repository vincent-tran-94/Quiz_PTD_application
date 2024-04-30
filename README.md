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
###  Partie Backend
- app.py # Application principale 
- models.py # Modélisation des données 
- mail.py #Procédure de confirmation de mail
- vizualisation.py #Visualisations des résultats sur les catégories
- template/ # Liste des pages 
- static/images # Liste des images
- static/videos # Liste des vidéos
- static/styles # Fichiers CSS
- static/JS #Fichiers de JavaScript 
- questions/ # Fichiers JSON contenant une série de questions*
- log_essais/ #Fichier de log qui permet de mettre à jour tout les mois le nombre d'essais par utilisateur
- .env Fichier de configuration pour les variables d'environnements
- config.cfg Fichier de configuration pour activer le serveur STMP du GMAIL

### Partie Frontend
- Framework (React,Vuejs,...)

## Formulaire pour la participation du concours du quiz
- nom 
- prenom 
- adresse 
- code_postal
- ville 
- pays
- niveau_etude 
- statut 
- centre_interet 
- choix_categorie 

## Base de données PostgreSQL
- participants.db # On dispose de 6 tables:
    - User : Nombre de participants ayant inscrit l'application du quiz
    - participant : Le nombre de participants ayant rempli le formulaire
    - reponse_participant : Le nombre de réponses effectués par un participant
    - contact: contact client des participants soumis dans l'application 
    - strip_customer: Client ayant payé un abonnement sur-mesure en l'utilisant l'API Stripe
    - parrainage : Parrain pour avoir le code de réduction pour plus tard on souhaitera de collaborer aux autres participants
    - apscheduler_job: Nombre de travailleurs qui permet de planifier les tâches lorsqu'on incrémente le nombre d'essais

## Installation et setup
- Version Python 3.11.7
- Docker
- PostgreSQL
- Stripe CLI

Tout d'abord, vous devez installer Postgresql et choisissez la dernière version: 
```
https://www.postgresql.org/download/
```

Dirigez vous à l'invite de commande sur Pgsql et connectez-vous à votre compte.
Ensuite, vous devez créer un ID de l'utilisateur avec votre mot de passe et votre nom de la base de données <br>
en lançant ces deux commandes: 
```
CREATE ROLE you_id_database WITH LOGIN PASSWORD 'you_password';
CREATE DATABASE you_name_database OWNER you_id_database;
```
Rendez-vous dans ce lien pour vous inscrire un compte sur strip et suivez les étapes pour la création du compte
"""
### A savoir que l'installation sur PgAdmin marche la connexion uniquement sur votre propre système
"""
```
https://www.postgresql.org/download/
```

Dirigez vous à l'invite de commande sur Pgsql et connectez-vous à votre compte.
Ensuite, vous devez créer un ID de l'utilisateur avec votre mot de passe et votre nom de la base de données <br>
en lançant ces deux commandes: 
```
CREATE ROLE you_id_database WITH LOGIN PASSWORD 'you_password';
CREATE DATABASE you_name_database OWNER you_id_database;
```

Importer le lien du projet et puis créez votre environnement virtuel
```
git clone https://github.com/Preserve-ton-Droit/Quiz_PTD_application.git
python3 -m venv env
source env/Scripts/activate
```
Diriger-vous vers flask_app
```
cd flask_app/ 
```

Installer les dépendances 
```
pip install -r requirements.txt 
```

Ajouter le fichier config.cfg et copier les informations ci-dessous:
```
MAIL_SERVER='smtp.gmail.com'
MAIL_USERNAME='asso.ptdlegalquiz@gmail.com'
MAIL_DEFAULT_SENDER = 'asso.ptdlegalquiz@gmail.com'  
MAIL_PASSWORD='qbrt vxbf vjnb ridl'
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
```

Ajouter le fichier .env et copier les informations ci-dessous:
```
[App]
HOST='0.0.0.0'
PORT='5000'
MAIL_ASSOCIATION_CONTACT='asso.ptdlegalquiz@gmail.com'
SECRET_KEY='you_secret_key' 

[Database]
ID_DATABASE="you_id_database"
PASSWORD_DATABASE="you_password" 
ADDRESS_IP="you_address_ip_database" Si vous êtes en local mettez localhost sinon mettre le nom de l'image de docker
NAME_DATABASE="you_name_database"

[STRIPE]
STRIPE_PUBLIC_KEY='you_key_public'
STRIPE_SECRET_KEY= 'you_secret_key'
STRIPE_SECRET_ENDPOINT='you_secret_endpoint_key'

ID_PRODUCT_BRONZE='YOU_ID_PRODUCT'
ID_PRODUCT_SILVER=''
ID_PRODUCT_GOLD=''
ID_TAXE_RATE='you_ID_TAX'
ID_COUPON='you_ID_COUPON'
```

Rendez-vous dans ce lien pour vous inscrire un compte sur strip et suivez les étapes pour créer votre premier compte de test
```
https://stripe.com/fr/connect
```
Sur une autre console, si vous êtes en local, lancez cette commande du stripe CLI.
```
stripe listen --forward-to http://localhost:5000/stripe_webhook --api-key YOU_API_KEY
```
Elle permet de démarrer un écouteur qui surveille les événements Stripe sur votre compte et les redirige vers un endpoint HTTP spécifié
Les webhooks vous permettent de recevoir des notifications en temps réel des événements sur votre compte Stripe, comme les paiements réussis, les abonnements créés, etc. Vous pouvez alors extraire les informations nécessaires, telles que le nom du produit et l'adresse du client, à partir des données fournies dans ces webhooks. Mettez votre API KEY pour activer le CLI du webhook

Lancer votre application Flask pour démarrer votre serveur à l'aide de docker
```
docker-compose build
```
```
docker-compose up -d
```
Sur une autre console pour avoir votre adresse IP de l'image sur Pgadmin, vous devez lancer cette ligne de commande pour récupérer son adresse IP 
```
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' flask_app-db-1
```
Si vous voulez arrêter les conteneurs 
```
docker-compose down 
```
