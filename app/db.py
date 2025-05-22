from flask_sqlalchemy import SQLAlchemy
import click
from config import BASE_DIR
import os


db = SQLAlchemy()


@click.command('insert-data')
def insert_data_command():

    with open(os.path.join(BASE_DIR, 'app', 'script.sql'), 'rb') as f:
        db.session.execute(f.read().decode())
