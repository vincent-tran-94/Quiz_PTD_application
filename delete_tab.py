from app import db,app

with app.app_context():
    db.drop_all()
    print("La table Participant a été supprimée avec succès.")
