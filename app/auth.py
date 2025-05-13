import datetime
import jwt

from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from typing import Callable


auth_bp = Blueprint('auth', __name__, url_prefix = '/auth')


@auth_bp.route('/login', methods = ('POST',))
def login():

    user_data = request.get_json()
    username = user_data.get('username')
    password = user_data.get('password')

    if username == 'admin' and password == 'password':
        token = jwt.encode(
            {
                'user': username,
                'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes = 30)
            },
            current_app.config["SECRET_KEY"],
            algorithm = "HS256"
        )
    
        return jsonify({
            "token": token
        }), 200
    
    return jsonify({
        "message": "Invalid username/password"
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
            current_user = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token has expired!"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "message": "Invalid token!"
            }), 401
        
        return f(current_user, *args, **kwargs)

    return decorated
    