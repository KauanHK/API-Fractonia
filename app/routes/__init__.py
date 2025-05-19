from flask import Blueprint
from . import player


routes_bp = Blueprint('routes', __name__)
routes_bp.register_blueprint(player.bp)


__all__ = [
    'routes_bp'
]
