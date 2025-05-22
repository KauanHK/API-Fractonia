from werkzeug.security import generate_password_hash, check_password_hash
from .db import db
import datetime
from typing import Any


class Player(db.Model):

    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(120), nullable = False, unique = True)
    password_hash = db.Column(db.String(128), nullable = False)
    level = db.Column(db.Integer, default = 1)
    health = db.Column(db.Integer, default = 100)
    total_time = db.Column(db.Float, default = 0)
    saved_at = db.Column(db.DateTime, default = datetime.datetime.now)
    create_at = db.Column(db.DateTime, default = datetime.datetime.now)
    
    current_phase_id = db.Column(db.Integer, db.ForeignKey('phase.id'), nullable = False, default = 1)
    current_phase = db.relationship('Phase', backref = 'players')

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
            'username': self.username,
            'email': self.email,
            'level': self.level,
            'health': self.health,
            'current_phase': self.current_phase,
            'total_time': self.total_time,
            'saved_at': self.saved_at,
            'create_at': self.create_at,
            'items': [item.to_dict() for item in PlayerItem.query.filter(PlayerItem.player_id == self.id)],
            'current_phase': self.current_phase.to_dict()
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

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description
        }

    def __repr__(self):
        return f'<Rarity {self.name}>'


class Item(db.Model):

    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(255))
    power = db.Column(db.Integer, default = 0)
    acquired_at = db.Column(db.DateTime, default = lambda: datetime.datetime.now(datetime.UTC))

    rarity_id = db.Column(db.Integer, db.ForeignKey('rarity.id'), nullable = False)
    rarity = db.relationship('Rarity', backref = 'items')

    def __init__(
        self,
        name: str,
        description: str,
        rarity_id: int,
        power: int = 0
    ) -> None:
        
        self.name = name
        self.description = description
        self.rarity_id = rarity_id
        self.power = power

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'power': self.power,
            'acquired_at': self.acquired_at,
            'rarity': self.rarity.name
        }


class PlayerItem(db.Model):

    __tablename__ = 'player_item'

    id = db.Column(db.Integer, primary_key = True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable = False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable = False)

    player = db.relationship('Player', backref = 'inventory')
    item = db.relationship('Item', backref = 'owned_by')

    def __init__(
        self,
        player_id: int,
        item_id: int
    ) -> None:
        
        self.player_id = player_id
        self.item_id = item_id
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'item': self.item.to_dict()
        }


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

    def __init__(self, name: str) -> None:
        self.name = name
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'name': self.id
        }

    def __repr__(self):
        return f'<Boss {self.name}>'


class Phase(db.Model):

    __tablename__ = 'phase'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    description = db.Column(db.String(255))

    boss_id = db.Column(db.Integer, db.ForeignKey('boss.id'), nullable = True)
    boss = db.relationship('Boss', backref = 'phases')

    def __init__(self, name: str, description: str = '', boss_id: int = None):
        self.name = name
        self.description = description
        self.boss_id = boss_id

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'boss': self.boss.name if self.boss else None
        }

    def __repr__(self):
        return f'<Phase {self.name}>'
