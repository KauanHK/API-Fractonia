from flask import Blueprint
from . import item, player


routes_bp = Blueprint('routes', __name__)

routes_bp.register_blueprint(player.bp)
routes_bp.register_blueprint(item.bp)


__all__ = [
    'routes_bp'
]
