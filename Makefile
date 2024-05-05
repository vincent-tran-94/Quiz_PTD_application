activate:
    source env/Scripts/activate

install:
    cd flask_app && pip install -r requirements.txt

run:
    python run.py