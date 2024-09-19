import os
from datetime import timedelta

id_database = "vincenttran"
password_database = "associationptd"
address_ip = "localhost"
name_database = "participants"

class Config:
    SECRET_KEY = '_5#y2L"F4Q8z\n\xec]/' 
    SQLALCHEMY_DATABASE_URI = f"postgresql://{id_database}:{password_database}@{address_ip}:5432/{name_database}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    HOST = os.getenv('HOST')  
    PORT = os.getenv('PORT')  
    MAIL_ASSOCIATION_CONTACT = os.getenv("MAIL_ASSOCIATION_CONTACT")
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    ID_PRODUCT_BRONZE = os.getenv('ID_PRODUCT_BRONZE')
    ID_PRODUCT_SILVER = os.getenv('ID_PRODUCT_SILVER')
    ID_PRODUCT_GOLD = os.getenv('ID_PRODUCT_GOLD')
    TAXE_RATE = os.getenv('ID_TAXE_RATE')
    STRIPE_SECRET_ENDPOINT = os.getenv('STRIPE_SECRET_ENDPOINT')
    COUPON_ID = os.getenv('ID_COUPON')
