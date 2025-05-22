from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import click
from config import BASE_DIR
import os


db = SQLAlchemy()


@click.command('insert-data')
def insert_data_command():

    with open(os.path.join(BASE_DIR, 'app', 'script.sql'), 'rb') as f:
        sql_script = f.read().decode()
    
    statements = sql_script.strip().split(';')

    with db.session.begin():
        for statement in statements:
            if statement.strip():
                db.session.execute(text(statement))

        usernames = ['kauan', 'martin', 'tiago', 'william', 'bob']

        for username in usernames:
            db.session.execute(
                text("INSERT INTO player (username, email, password_hash, current_phase_id) VALUES (:username, :email, :password_hash, :current_phase_id)"),
                {
                    'username': username,
                    'email': f'{username}@gmail.com',
                    'password_hash': generate_password_hash('123'),
                    'current_phase_id': 1
                }
            )
