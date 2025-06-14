from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from ..db import db
from ..models import Player, Item, PlayerAchievement, PhaseProgress, PlayerItem, Achievement
from ..auth import token_required, admin_required, validate_access
from flask import abort
from datetime import datetime


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

    if validate_access(id, silent = True):
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
    player: Player = Player.query.get_or_404(id)
    return player.to_dict()


@bp.route('/<int:id>/items')
@token_required
def player_items(id: int):
    items = PlayerItem.query.filter_by(player_id = id)
    return jsonify({
        'items': [item.to_dict() for item in items],
        'total': items.count()
    })


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


@bp.route('/<int:id>/items/<int:item_id>', methods=['DELETE'])
@token_required
def remove_item(id: int, item_id: int):
    player_item = PlayerItem.query.filter_by(player_id=id, item_id=item_id).first_or_404()
    db.session.delete(player_item)
    db.session.commit()
    return jsonify({
        'message': f'Item {item_id} removido do jogador {id} com sucesso.'
    }), 200


@bp.route('/<int:id>/achievements')
@token_required
def player_achievements(id: int):
    Player.query.get_or_404(id)
    achievements = PlayerAchievement.query.filter_by(player_id=id).all()
    return [achievement.to_dict() for achievement in achievements]


@bp.route('/<int:id>/phases', methods=['GET'])
@token_required
def player_phases(id: int):
    """Lista todas as fases completadas pelo jogador"""
    phases = PhaseProgress.query.filter_by(player_id=id).all()
    return jsonify({
        'phases': [phase.to_dict() for phase in phases],
        'total': len(phases)
    })


@bp.route('/<int:id>/phases', methods=['POST'])
@token_required
def complete_phase(id: int):
    """Registra conclusão de uma fase pelo jogador"""
    data = request.get_json()
    
    if 'phase_id' not in data:
        abort(400, description="O ID da fase é obrigatório")
    
    # Verifica se o jogador já completou esta fase
    existing = PhaseProgress.query.filter_by(
        player_id=id,
        phase_id=data['phase_id']
    ).first()
    
    if existing:
        return jsonify({
            'message': 'Fase já completada anteriormente',
            'progress': existing.to_dict()
        }), 200
    
    # Cria novo progresso
    progress = PhaseProgress(
        player_id=id,
        phase_id=data['phase_id'],
        completed=True,
        completed_at=datetime.utcnow()
    )
    
    db.session.add(progress)
    db.session.commit()
    
    return jsonify({
        'message': 'Progresso na fase registrado com sucesso',
        'progress': progress.to_dict()
    }), 201

# ================================================
# Rotas para Conquistas
# ================================================


@bp.route('/<int:id>/achievements/progress', methods=['POST'])
@token_required
def update_achievement_progress(id: int):
    """Atualiza o progresso em uma conquista"""
    
    payload = request.get_json()
    if 'achievement_id' not in payload:
        abort(400, description="Campo obrigatório: 'achievement_id'")
    
    achievement_id = payload['achievement_id']
    achievement = Achievement.query.get_or_404(achievement_id)
    
    # Busca ou cria o progresso na conquista
    player_ach = PlayerAchievement.query.filter_by(
        player_id = id,
        achievement_id = achievement_id
    ).first()
    
    if not player_ach:
        player_ach = PlayerAchievement(
            player_id = id,
            achievement_id = achievement_id,
        )
        db.session.add(player_ach)

        # Aplica recompensas
        player: Player = Player.query.get(id)
        player.coins += achievement.reward_coins
    
    db.session.commit()
    
    return jsonify({
        'message': 'Progresso na conquista atualizado',
        'achievement': player_ach.to_dict()
    }), 200

# ================================================
# Rotas para Batalhas
# ================================================


@bp.route('/<int:id>/battles', methods=['GET'])
@token_required
def player_battles(id: int):
    """Lista todas as batalhas do jogador"""
    battles = Battle.query.filter_by(player_id=id).order_by(Battle.created_at.desc()).all()
    return jsonify({
        'battles': [battle.to_dict() for battle in battles],
        'total': len(battles)
    })


@bp.route('/<int:id>/battles', methods=['POST'])
@token_required
def record_battle(id: int):
    """Registra uma nova batalha para o jogador"""
    data = request.get_json()
    
    required_fields = ['result']
    if any(field not in data for field in required_fields):
        abort(400, description="O resultado da batalha é obrigatório")
    
    # Cria nova batalha
    battle = Battle(
        player_id=id,
        result=data['result'],
        boss_id=data.get('boss_id'),
        created_at=datetime.utcnow()
    )
    
    db.session.add(battle)
    db.session.commit()
    
    return jsonify({
        'message': 'Batalha registrada com sucesso',
        'battle': battle.to_dict()
    }), 201

# ================================================
# Rotas para Itens (atualização)
# ================================================


@bp.route('/<int:player_id>/items/<int:item_id>', methods=['PUT'])
@token_required
def update_player_item(player_id: int, item_id: int):
    """Atualiza um item do jogador (ex: equipar)"""
    player_item = PlayerItem.query.filter_by(
        player_id=player_id,
        item_id=item_id
    ).first_or_404()
    
    data = request.get_json()
    
    # Atualiza campos permitidos
    if 'is_equipped' in data:
        player_item.is_equipped = bool(data['is_equipped'])
    
    if 'durability' in data:
        player_item.durability = int(data['durability'])
    
    if 'slot' in data and data['slot'] in ['weapon', 'head', 'chest', 'legs', 'accessory']:
        player_item.slot = data['slot']
    
    db.session.commit()
    
    return jsonify({
        'message': f'Item {item_id} atualizado para o jogador {player_id}',
        'item': player_item.to_dict()
    }), 200
