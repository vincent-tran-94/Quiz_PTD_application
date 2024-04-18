from celery_worker import create_app
from celery import shared_task
from celery.schedules import crontab

flask_app = create_app()
celery_app = flask_app.extensions["celery"]

# Définir une tâche Celery
@shared_task(name="nom_de_votre_tache")
def votre_tache():
    # Votre code de tâche ici
    return "Successful !"

# Exemple d'appel de la tâche depuis Flask
@flask_app.route('/run_task')
def run_task():
    # Appel de la tâche Celery
    votre_tache.delay()
    return "Tâche lancée avec succès"

if __name__ == '__main__':
    flask_app.run()

