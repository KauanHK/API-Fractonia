from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import timezone
import enum

db = SQLAlchemy()

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

# Relação Many-to-Many Player - Item
player_items = db.Table('player_items',
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key = True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key = True)
)


class ResultType(enum.Enum):
    WIN = 'win'
    LOSS = 'loss'
    FLEE = 'flee'


class Player(db.Model):
    __tablename__ = 'player'
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    level = db.Column(db.Integer, default = 1) 
    experience = db.Column(db.BigInteger, default = 0)
    coins = db.Column(db.BigInteger, default = 0)
    created_at = db.Column(db.DateTime, default = utcnow)
    saved_at = db.Column(db.DateTime, default = utcnow)
    
    achievements = db.relationship('PlayerAchievement', backref = 'player', lazy = True)
    phase_progresses = db.relationship('PhaseProgress', backref = 'player', lazy = True)
    battles = db.relationship('Battle', backref = 'player', lazy = True)
    items = db.relationship('Item', secondary = player_items, backref = 'owners', lazy = True)

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
            'created_at': self.created_at.isoformat()
        }


class Achievement(db.Model):
    __tablename__ = 'achievement'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique = True, nullable = False)
    description = db.Column(db.String(255), nullable = False)
    reward_coins = db.Column(db.Integer, default = 0)
    icon = db.Column(db.String(255))
    criteria = db.Column(db.String(100), nullable = False)
    target_value = db.Column(db.Integer, nullable = False)
    reward_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable = True)
    
    players = db.relationship('PlayerAchievement', backref = 'achievement', lazy = True)
    reward_item = db.relationship('Item', backref = 'achievements', lazy = True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'reward_coins': self.reward_coins,
            'icon': self.icon,
            'criteria': self.criteria,
            'target_value': self.target_value,
            'reward_item_id': self.reward_item_id
        }


class PlayerAchievement(db.Model):
    __tablename__ = 'player_achievement'
    
    id = db.Column(db.Integer, primary_key = True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable = False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable = False)
    progress = db.Column(db.Integer, default = 0)
    completed = db.Column(db.Boolean, default = False)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'achievement': self.achievement.to_dict(),
            'progress': self.progress,
            'target': self.achievement.target_value,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Phase(db.Model):
    __tablename__ = 'phase'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    
    progresses = db.relationship('PhaseProgress', backref = 'phase', lazy = True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class PhaseProgress(db.Model):
    __tablename__ = 'phase_progress'
    
    id = db.Column(db.Integer, primary_key = True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable = False)
    phase_id = db.Column(db.Integer, db.ForeignKey('phase.id'), nullable = False)
    completed = db.Column(db.Boolean, default = False)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'phase': self.phase.to_dict(),
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Battle(db.Model):
    __tablename__ = 'battle'
    
    id = db.Column(db.Integer, primary_key = True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable = False)
    result = db.Column(db.Enum(ResultType), default = ResultType.WIN)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'result': self.result.value,
            'created_at': self.created_at.isoformat()
        }


class Item(db.Model):
    __tablename__ = 'item'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    achievement_reward = db.Column(db.Boolean, default = False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_reward': self.achievement_reward
        }
