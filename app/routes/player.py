from flask import Blueprint, request
from werkzeug.security import generate_password_hash
from ..db import db
from ..models import Player, PlayerItem, Item
from ..auth import token_required


bp = Blueprint('player', __name__, url_prefix = '/player')


@bp.route('/all')
def index():
    return [player.to_dict() for player in Player.query.all()]


@bp.route('/new', methods = ['POST'])
def new_player():
    
    player_json = request.get_json()
    print(player_json)

    player = Player(
        username = player_json['username'],
        email = player_json['email'],
        password_hash = generate_password_hash(player_json['password'])
    )

    db.session.add(player)
    db.session.commit()

    return player.to_dict()


@bp.route('/<int:id>')
@token_required
def player(current_user_id: int, id: int):

    if id != current_user_id:
        return {
            'message': "You don't have access to this page"
        }, 403

    return Player.query.get_or_404(id).to_dict()


@bp.route('/<int:id>/items')
def player_items(id: int):
    return [item.to_dict() for item in PlayerItem.query.filter(PlayerItem.player_id == id)]


@bp.route('/<int:id>/new-item')
def new_item(id: int):

    item_id = request.json()['item_id']

    # Verificar se existem
    Player.query.get_or_404(id)
    Item.query.get_or_404(item_id)
    
    player_item = PlayerItem(
        player_id = id,
        item_id = item_id
    )

    db.session.add(player_item)
    db.session.commit()

    return player_item.to_dict()
