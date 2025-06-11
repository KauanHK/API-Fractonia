from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from ..db import db
from ..models import Player, Item, PlayerAchievement, PhaseProgress
from ..auth import token_required, admin_required, validate_access
from flask import abort


bp = Blueprint('players', __name__, url_prefix='/players')


@bp.route('/')
@admin_required
def index():
    players: list[Player] = Player.query.all()
    return jsonify({
        'players': [player.to_dict() for player in players],
        'total': len(players),
    })


@bp.route('/', methods=['POST'])
def new_player():

    data = request.get_json()
    
    if any(attr not in data for attr in ['username', 'email', 'password']):
        abort(400, description = "Campos obrigatórios estão faltando: username, email ou password")

    if Player.query.filter_by(username = data['username']).first():
        abort(400, description = "Nome de usuário já existe")

    if Player.query.filter_by(email=data['email']).first():
        abort(400, description = "Email já existe")

    player = Player(
        username = data['username'],
        email = data['email'],
        password = data['password']
    )

    db.session.add(player)
    db.session.commit()

    return player.to_dict(), 201


@bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_player(id: int):

    player: Player = Player.query.get_or_404(id)

    if validate_access(silent = True):
        abort(403, description = "Você não tem permissão para atualizar este jogador")

    data = request.get_json()

    for field in ('username', 'email'):
        if not field in data:
            continue
        if Player.query.filter(getattr(Player, field) == data[field]).first():
            abort(400, descriptions = "Nome de usuário já existe")
        player.username = data['username']

    if 'password' in data:
        player.set_password(data['password'])

    for attr in ('level', 'experience', 'coins', 'saved_at'):
        if attr in data:
            setattr(player, attr, data[attr])

    db.session.commit()
    return jsonify({
        'message': f'Jogador {id} atualizado com sucesso.',
        'player': player.to_dict()
    }), 200


@bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_player(id: int):
    player = Player.query.get_or_404(id)
    db.session.delete(player)
    db.session.commit()
    return jsonify({
        'message': f'Jogador {id} deletado com sucesso.'
    }), 200


@bp.route('/<int:id>')
@token_required
def player(id: int):
    player = Player.query.get_or_404(id)
    return player.to_dict()


@bp.route('/<int:id>/items')
@token_required
def player_items(id: int):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    items = PlayerItem.query.filter_by(player_id=id).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [item.to_dict() for item in items.items],
        'total': items.total,
        'pages': items.pages,
        'current_page': page
    })

# Adiciona um item a um jogador
@bp.route('/<int:id>/items', methods=['POST'])
@token_required
def new_item(id: int):
    data = request.get_json()
    item_id = data.get('item_id')
    if not item_id:
        abort(400, description="ID do item é obrigatório")
    Player.query.get_or_404(id)
    Item.query.get_or_404(item_id)
    if PlayerItem.query.filter_by(player_id=id, item_id=item_id).first():
        abort(400, description="Item já associado ao jogador")
    player_item = PlayerItem(player_id=id, item_id=item_id)
    db.session.add(player_item)
    db.session.commit()
    return player_item.to_dict(), 201

# Remove um item de um jogador
@bp.route('/<int:id>/items/<int:item_id>', methods=['DELETE'])
@token_required
def remove_item(id: int, item_id: int):
    player_item = PlayerItem.query.filter_by(player_id=id, item_id=item_id).first_or_404()
    db.session.delete(player_item)
    db.session.commit()
    return jsonify({
        'message': f'Item {item_id} removido do jogador {id} com sucesso.'
    }), 200

# Retorna as estatísticas de progressão de nível de um jogador
@bp.route('/<int:id>/stats')
@token_required
def stats(id: int):
    Player.query.get_or_404(id)
    stats = LevelProgress.query.filter_by(player_id=id).all()
    return [stat.to_dict() for stat in stats]

# Retorna as conquistas de um jogador
@bp.route('/<int:id>/achievements')
@token_required
def player_achievements(id: int):
    Player.query.get_or_404(id)
    achievements = PlayerAchievement.query.filter_by(player_id=id).all()
    return [achievement.to_dict() for achievement in achievements]

# Retorna os progressos de fases de um jogador
@bp.route('/<int:id>/phases')
@token_required
def player_phases(id: int):
    Player.query.get_or_404(id)
    phases = PhaseProgress.query.filter_by(player_id=id).all()
    return [phase.to_dict() for phase in phases]
