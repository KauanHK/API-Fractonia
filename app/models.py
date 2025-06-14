from werkzeug.security import generate_password_hash, check_password_hash
from .db import db
from datetime import datetime, timezone
import enum


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResultType(enum.Enum):
    WIN = 'win'
    LOSS = 'loss'
    FLEE = 'flee'


class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.BigInteger, default=0)
    coins = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
    saved_at = db.Column(db.DateTime, default=utcnow)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'level': self.level,
            'experience': self.experience,
            'coins': self.coins,
            'created_at': self.created_at.isoformat(),
        }


class Achievement(db.Model):
    __tablename__ = 'achievement'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    reward_coins = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'reward_coins': self.reward_coins,
        }


class PlayerAchievement(db.Model):
    __tablename__ = 'player_achievement'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'achievement_id': self.achievement_id,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Phase(db.Model):
    __tablename__ = 'phase'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    boss_id = db.Column(db.Integer, db.ForeignKey('boss.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'boss_id': self.boss_id,
        }


class PhaseProgress(db.Model):
    __tablename__ = 'phase_progress'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    phase_id = db.Column(db.Integer, db.ForeignKey('phase.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'phase_id': self.phase_id,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Battle(db.Model):
    __tablename__ = 'battle'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    boss_id = db.Column(db.Integer, db.ForeignKey('boss.id'))
    result = db.Column(db.Enum(ResultType), default=ResultType.WIN)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'boss_id': self.boss_id,
            'result': self.result.value,
            'created_at': self.created_at.isoformat()
        }


class Item(db.Model):
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name: str) -> None:
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class PlayerItem(db.Model):
    __tablename__ = 'player_items'

    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)

    def __init__(self, player_id, item_id):
        self.player_id = player_id
        self.item_id = item_id

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'item_id': self.item_id,
        }


class Boss(db.Model):
    __tablename__ = 'boss'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    health = db.Column(db.Integer, nullable=False, default=500)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'health': self.health
        }
