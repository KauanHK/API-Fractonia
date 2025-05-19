from flask import Blueprint, request
from werkzeug.security import generate_password_hash
from ..db import db
from ..models import Player


bp = Blueprint('player', __name__, url_prefix = '/player')


@bp.route('/all')
def index():
    return [player.to_dict() for player in Player.query.all()]


@bp.route('/new', methods = ['POST'])
def new_player():
    
    player_data = request.get_json()
    print(player_data)

    player = Player(
        username = player_data['username'],
        email = player_data['email'],
        password_hash = generate_password_hash(player_data['password'])
    )

    db.session.add(player)
    db.session.commit()

    return player.to_dict()


@bp.route('/<int:id>')
def player(id: int):
    return Player.query.get_or_404(id).to_dict()


@bp.route('/<int:id>/stats')
def player_stats(id: int):
    ...


@bp.route('/<int:id>/items')
def player_items(id: int):
    ...


@bp.route('/<int:id>/new-item')
def new_item(id: int):
    ...
