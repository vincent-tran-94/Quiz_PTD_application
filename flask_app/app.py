from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from config import Config
import stripe

app = Flask(__name__, template_folder='template', static_url_path='/static')

# Charger les configurations depuis config.py
app.config.from_object(Config)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

jobstore = SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
jobstores = {
    'default': jobstore
}
scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults={'misfire_grace_time': None})

stripe.api_key = app.config['STRIPE_SECRET_KEY']


