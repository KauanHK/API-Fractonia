from werkzeug.security import generate_password_hash, check_password_hash
from .db import db
import datetime


class Player(db.Model):

    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(120), nullable = False, unique = True)
    password_hash = db.Column(db.String(128), nullable = False)
    level = db.Column(db.Integer, default = 1)
    health = db.Column(db.Integer, default = 100)
    create_at = db.Column(db.DateTime, default = datetime.datetime.now(datetime.UTC))

    items = db.relationship('Item', backref = 'player', lazy = True)

    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str
    ) -> None:
        
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.username,
            'email': self.email,
            'created_at': self.create_at
        }
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Player {self.username}>'


class Rarity(db.Model):

    __tablename__ = 'rarity'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), unique = True, nullable = False)
    color = db.Column(db.String(20))
    description = db.Column(db.String(100))

    items = db.relationship('Item', backref = 'rarity', lazy = True)

    def __repr__(self):
        return f'<Rarity {self.name}>'


class Item(db.Model):

    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    type = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(255))
    power = db.Column(db.Integer, default = 0)
    rarity_id = db.Column(db.Integer, db.ForeignKey('rarity.id'), nullable = False)
    acquired_at = db.Column(db.DateTime, default = datetime.datetime.now(datetime.UTC))

    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)


class LevelProgress(db.Model):

    __tablename__ = 'level_progress'

    id = db.Column(db.Integer, primary_key = True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable = False)
    phase_number = db.Column(db.Integer, nullable = False)
    time_spent = db.Column(db.Float)
    completed_at = db.Column(db.DateTime, default = datetime.datetime.now(datetime.UTC))

    player = db.relationship('Player', backref = 'level_progress')

    def __repr__(self):
        return f'<LevelProgress Player {self.player_id} Fase {self.phase_number}>'


class Boss(db.Model):

    __tablename__ = 'boss'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)

    def __repr__(self):
        return f'<Boss {self.name}>'


class GameProgress(db.Model):

    __tablename__ = 'game_progress'

    id = db.Column(db.Integer, primary_key = True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable = False)
    current_phase = db.Column(db.Integer, nullable = False)
    total_time = db.Column(db.Float)
    saved_at = db.Column(db.DateTime, default = datetime.datetime.now(datetime.UTC))

    player = db.relationship('Player', backref = 'game_progress')

    def __repr__(self):
        return f'<GameProgress Player {self.player_id}>'
