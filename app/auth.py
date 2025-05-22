import datetime
import jwt
from .models import Player
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from typing import Callable


auth_bp = Blueprint('auth', __name__, url_prefix = '/auth')


@auth_bp.route('/login', methods = ('POST',))
def login():

    user_data = request.get_json()
    username = user_data.get('username')
    password = user_data.get('password')

    player = Player.query.filter(Player.username == username).one_or_none()
    if player is None:
        return {
            'message': 'Invalid username'
        }
    
    if not check_password_hash(player.password_hash, password):
        return {
            'message': 'Invalid username/password'
        }

    token = jwt.encode(
        {
            'id': player.id,
            'username': username,
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes = 30)
        },
        current_app.config["SECRET_KEY"],
        algorithm = "HS256"
    )
    
    return jsonify({
        "token": token
    }), 401


def token_required(f: Callable):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({
                "message": "Token is missing!"
            }), 401
        
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms = ['HS256'])
            current_user_id = data['id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token has expired!"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "message": "Invalid token!"
            }), 401
        
        return f(current_user_id, *args, **kwargs)

    return decorated
    