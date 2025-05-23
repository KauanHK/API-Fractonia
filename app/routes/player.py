from flask import Blueprint, request
from werkzeug.security import generate_password_hash
from ..db import db
from ..models import Player, PlayerItem, Item
from ..auth import token_required, validate_access, admin_required


bp = Blueprint('player', __name__, url_prefix = '/player')


@bp.route('/all')
@admin_required
def index():
    return [player.to_dict() for player in Player.query.all()]


@bp.route('/new', methods = ['POST'])
@admin_required
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
    validate_access(current_user_id, id)

    return Player.query.get_or_404(id).to_dict()


@bp.route('/<int:id>/items')
@token_required
def player_items(current_user_id: int, id: int):
    validate_access(current_user_id, id)
    return [item.to_dict() for item in PlayerItem.query.filter(PlayerItem.player_id == id)]


@bp.route('/<int:id>/new-item')
@token_required
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
