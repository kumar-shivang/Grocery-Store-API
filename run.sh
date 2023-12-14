python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
redis-server
celery -A app.celery worker --loglevel=info -B
flask run