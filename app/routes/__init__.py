from flask import Blueprint
from . import item, player, phase, boss, achievements, battle


routes_bp = Blueprint('routes', __name__)

routes_bp.register_blueprint(player.bp)
routes_bp.register_blueprint(item.bp)
routes_bp.register_blueprint(phase.bp)
routes_bp.register_blueprint(boss.bp)
routes_bp.register_blueprint(achievements.bp)
routes_bp.register_blueprint(battle.bp)

__all__ = [
    'routes_bp'
]
