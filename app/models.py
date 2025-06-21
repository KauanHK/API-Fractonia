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
            'experience': self.experience,
            'coins': self.coins,
            'created_at': self.created_at.isoformat(),
            'saved_at': self.saved_at.isoformat() if self.saved_at else None
        }


class Achievement(db.Model):
    __tablename__ = 'achievement'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    xp_required = db.Column(db.BigInteger, default = 0)
    reward_coins = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'reward_coins': self.reward_coins,
            'xp_required': self.xp_required
        }


class PlayerAchievement(db.Model):
    __tablename__ = 'player_achievement'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default = utcnow)

    player = db.relationship('Player', backref='achievements', lazy=True)
    achievement = db.relationship('Achievement', backref='players', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'player': self.player.to_dict(),
            'achievement': self.achievement.to_dict(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Phase(db.Model):
    __tablename__ = 'phase'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    boss_id = db.Column(db.Integer, db.ForeignKey('boss.id'))
    reward_coins = db.Column(db.Integer, default=0)
    reward_experience = db.Column(db.BigInteger, default=0)

    boss = db.relationship('Boss', backref='phases', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'boss': self.boss.to_dict(),
            'reward_coins': self.reward_coins,
            'reward_experience': self.reward_experience
        }


class PhaseProgress(db.Model):
    __tablename__ = 'phase_progress'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    phase_id = db.Column(db.Integer, db.ForeignKey('phase.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    player = db.relationship('Player', backref='phase_progress', lazy=True)
    phase = db.relationship('Phase', backref='progress', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'player': self.player.to_dict(),
            'phase': self.phase.to_dict(),
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Battle(db.Model):
    __tablename__ = 'battle'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    boss_id = db.Column(db.Integer, db.ForeignKey('boss.id'))
    result = db.Column(db.Enum(ResultType), default=ResultType.WIN)
    reward_coins = db.Column(db.Integer, default=0)
    reward_experience = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)

    player = db.relationship('Player', backref='battles', lazy=True)
    boss = db.relationship('Boss', backref='battles', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'player': self.player.to_dict(),
            'boss': self.boss.to_dict(),
            'result': self.result.value,
            'created_at': self.created_at.isoformat(),
            'reward_coins': self.reward_coins,
            'reward_experience': self.reward_experience
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

    player = db.relationship('Player', backref='items', lazy=True)
    item = db.relationship('Item', backref='players', lazy=True)

    def to_dict(self):
        return {
            'player': self.player.to_dict(),
            'item_id': self.item.to_dict()
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
