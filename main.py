from flask import Flask
from waitress import serve
import psycopg2
import os

app = Flask(__name__)

@app.route("/")
def index():
    username = os.environ.get('USER', 'runner')

    connection = psycopg2.connect(
        host="127.0.0.1",
        database="appdb",
        user=username)

    cursor = connection.cursor()
    cursor.execute('SELECT version()')
    db_version = cursor.fetchone()
    cursor.close()
    connection.close()

    return f"Hello from Python! PostgreSQL database version: {db_version}"

serve(app, host='0.0.0.0', port=5000, url_scheme='https')
