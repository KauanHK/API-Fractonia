from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from ..db import db
from ..models import Player, PlayerItem, Item, LevelProgress
from ..auth import token_required, admin_required


bp = Blueprint('players', __name__, url_prefix = '/players')


@bp.route('/')
@admin_required
def index():
    return [player.to_dict() for player in Player.query.all()]


@bp.route('/', methods = ['POST'])
@admin_required
def new_player():
    
    player_json = request.get_json()

    player = Player(
        username = player_json['username'],
        email = player_json['email'],
        password_hash = generate_password_hash(player_json['password'])
    )

    db.session.add(player)
    db.session.commit()

    return player.to_dict()


@bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_player(id: int):

    player = Player.query.get_or_404(id)

    data_json = request.get_json()

    attributes = [
        'username',
        'email',
        'level',
        'health',
        'total_time',
        'saved_at',
        'current_phase_id'
    ]

    for attr in attributes:
        if data_json.get(attr):
            setattr(player, attr, data_json[attr])

    db.session.commit()

    return jsonify({'message': f'Player {id} updated successfully.', 'player': player.to_dict()}), 200


@bp.route('/<int:id>', methods = ['DELETE'])
@token_required
def delete_player(id: int):

    player = Player.query.get_or_404(id)
    db.session.delete(player)
    db.session.commit()

    return jsonify({
        'message': f'Player {id} deleted successfully.'
    })


@bp.route('/<int:id>')
@token_required
def player(id: int):
    return Player.query.get_or_404(id).to_dict()


@bp.route('/<int:id>/items')
@token_required
def player_items(id: int):
    return [item.to_dict() for item in PlayerItem.query.filter(PlayerItem.player_id == id)]


@bp.route('/<int:id>/items', methods = ['POST'])
@token_required
def new_item(id: int):

    item_id = request.json['item_id']

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


@bp.route('/<int:id>/stats')
@token_required
def stats(id: int):

    Player.query.get_or_404(id)

    player_stats = LevelProgress.query.filter(LevelProgress.player_id == id).all()

    stats_json = []
    for stat in player_stats:
        stats_json.append(stat.to_dict())
    
    return stats_json
    