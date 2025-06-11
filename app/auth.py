import datetime
import jwt
from .models import Player
from functools import wraps
from flask import Blueprint, request, jsonify, current_app, abort
from werkzeug.security import check_password_hash
from typing import Callable, NoReturn, overload


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
    })


def get_current_user_id(token: str | None = None) -> int:

    if token is None:
        token = get_token()
    try:
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms = ['HS256'])
        return data['id']
    
    except jwt.ExpiredSignatureError:
        abort(401, "Token has expired!")
    
    except jwt.InvalidTokenError:
        abort(401, "Invalid token!")

    
def get_token() -> str:

    token = request.headers.get('x-access-token')
    if token is None:
        abort(401, "Token is missing!")
    return token


def token_required(f: Callable):

    @wraps(f)
    def decorated(id: int, *args, **kwargs):

        current_user_id = get_current_user_id()
        validate_access(current_user_id, id)
        return f(id, *args, **kwargs)

    return decorated


def admin_required(f: Callable):

    @wraps(f)
    def decorated(*args, **kwargs):
        
        current_user_id = get_current_user_id()
        
        if not is_admin(current_user_id):
            abort(403, "You don't have access to this page")
        
        return f(*args, **kwargs)

    return decorated


def is_admin(user_id: int):
    player = Player.query.get_or_404(user_id)
    return player.username == 'admin'


@overload
def validate_access(current_user_id: int, user_id: int, silent: bool = False) -> NoReturn: ...
@overload
def validate_access(current_user_id: int, user_id: int, silent: bool = True) -> bool: ...

def validate_access(current_user_id: int, user_id: int, silent: bool = False) -> bool:

    if current_user_id != user_id and not is_admin(current_user_id):
        abort(403, "Você não tem acesso a essa página")
    return None
