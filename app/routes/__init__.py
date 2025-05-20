from flask import Blueprint
from . import player, items


routes_bp = Blueprint('routes', __name__)

routes_bp.register_blueprint(player.bp)
routes_bp.register_blueprint(items.bp)


__all__ = [
    'routes_bp'
]
