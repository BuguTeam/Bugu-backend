.\venv\Scripts\activate
set FLASK_CONFIG=development
set FLASK_APP=run.py
flask db migrate
flask db upgrade
flask run