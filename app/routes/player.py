from flask import Blueprint, request, jsonify
from ..db import db
from ..models import Player, Item, PlayerAchievement, PhaseProgress, PlayerItem, Achievement, Battle, ResultType, Phase, utcnow
from ..auth import token_required, admin_required, validate_access, get_current_user_id, is_admin
from flask import abort
from datetime import datetime


bp = Blueprint('players', __name__, url_prefix='/players')


def _check_and_grant_achievements(player: Player):
    """
    Verifica e concede conquistas com base na experiência total do jogador.
    """
    all_achievements: list[Achievement] = Achievement.query.all()
    player_achievements_ids: set[int] = {pa.achievement_id for pa in player.achievements}

    for achievement in all_achievements:
        if player.experience >= achievement.xp_required and achievement.id not in player_achievements_ids:
            new_player_achievement = PlayerAchievement(
                player_id=player.id,
                achievement_id=achievement.id
            )
            db.session.add(new_player_achievement)
            player.coins += achievement.reward_coins


@bp.route('/<int:id>/insignia')
@token_required
def get_player_main_insignia(id: int):
    """Retorna a insígnia/conquista de maior prestígio do jogador."""
    
    player: Player = Player.query.get_or_404(id)

    # Encontra a conquista de maior XP requerido que o jogador possui.
    main_insignia = db.session.query(Achievement)\
        .join(PlayerAchievement, PlayerAchievement.achievement_id == Achievement.id)\
        .filter(PlayerAchievement.player_id == id)\
        .order_by(Achievement.xp_required.desc())\
        .first()

    if not main_insignia:
        return jsonify({
            'message': 'Este jogador ainda não possui nenhuma insígnia.'
        }), 404

    return jsonify({
        'insignia': main_insignia.to_dict(),
        'player': player.username
    })


@bp.route('/')
@admin_required
def index():
    players: list[Player] = Player.query.all()
    return jsonify({
        'players': [player.to_dict() for player in players],
        'total': len(players),
    })


@bp.route('/ranking')
def ranking():
    """Retorna o ranking geral dos jogadores baseado na experiência."""
    players: list[Player] = Player.query.order_by(Player.experience.desc()).all()
    return jsonify([
        {
            'rank': index + 1,
            'id': player.id,
            'username': player.username,
            'experience': player.experience
        }
        for index, player in enumerate(players)
    ])


@bp.route('/<int:id>/phases', methods=['POST'])
@token_required
def complete_phase(id: int):

    data = request.get_json()
    if 'phase_id' not in data:
        abort(400, description = "O ID da fase é obrigatório")

    player: Player = Player.query.get_or_404(id)
    phase: Phase = Phase.query.get_or_404(data['phase_id'])
    
    if PhaseProgress.query.filter_by(player_id = id, phase_id = data['phase_id']).first():
        return jsonify({'message': 'Fase já completada anteriormente'}), 200
    
    if phase.reward_coins:
        player.coins += phase.reward_coins
    if phase.reward_experience:
        player.experience += phase.reward_experience

    _check_and_grant_achievements(player)
    
    progress = PhaseProgress(
        player_id = id, phase_id = data['phase_id'], completed=True, completed_at = utcnow()
    )
    db.session.add(progress)
    db.session.commit()
    
    return jsonify({
        'message': f'Fase {phase.name} completada! Recompensas recebidas.',
        'player_status': player.to_dict()
    }), 201


@bp.route('/', methods=['POST'])
def new_player():
    data = request.get_json()
    if any(attr not in data for attr in ['username', 'email', 'password']):
        abort(400, description="Campos obrigatórios estão faltando: username, email ou password")
    if Player.query.filter_by(username=data['username']).first():
        abort(400, description="Nome de usuário já existe")
    if Player.query.filter_by(email=data['email']).first():
        abort(400, description="Email já existe")
    player = Player(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    db.session.add(player)
    db.session.commit()
    return player.to_dict(), 201


@bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_player(id: int):

    player: Player = Player.query.get_or_404(id)
    data = request.get_json()
    if 'username' in data and data['username'] != player.username:
        if Player.query.filter_by(username=data['username']).first():
            abort(400, description="Nome de usuário já existe")
        player.username = data['username']
    if 'email' in data and data['email'] != player.email:
        if Player.query.filter_by(email=data['email']).first():
            abort(400, description="Email já existe")
        player.email = data['email']
    if 'password' in data:
        player.set_password(data['password'])
    if is_admin(get_current_user_id()):
        for attr in ('experience', 'coins'):
            if attr in data:
                setattr(player, attr, data[attr])
    player.saved_at = utcnow()
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
    items: list[Item] = PlayerItem.query.filter_by(player_id = id)
    return jsonify({
        'items': [item.to_dict() for item in items],
        'total': items.count()
    })


@bp.route('/<int:id>/items', methods=['POST'])
@token_required
def add_player_item(id: int):

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
    achievements: list[Achievement] = PlayerAchievement.query.filter_by(player_id=id).all()
    return jsonify([achievement.to_dict() for achievement in achievements])


@bp.route('/<int:id>/battles', methods=['POST'])
@token_required
def record_battle(id: int):
    """Registra uma nova batalha e, em caso de vitória, aplica recompensas e verifica conquistas."""
    
    data = request.get_json()
    if 'result' not in data:
        abort(400, description="O resultado ('result') da batalha é obrigatório")

    player: Player = Player.query.get_or_404(id)
    
    reward_coins = data.get('reward_coins', 0)
    reward_experience = data.get('reward_experience', 0)

    battle = Battle(
        player_id = id,
        result = data['result'],
        boss_id = data.get('boss_id'),
        reward_coins = reward_coins,
        reward_experience = reward_experience
    )
    
    # Se o jogador venceu, aplica as recompensas e verifica conquistas
    if battle.result == ResultType.WIN:
        player.coins += reward_coins
        player.experience += reward_experience
        _check_and_grant_achievements(player)

    db.session.add(battle)
    db.session.commit()

    return jsonify({
        'message': 'Batalha registrada com sucesso!',
        'battle_details': battle.to_dict(),
        'player_status': player.to_dict()
    }), 201


@bp.route('/<int:id>/phases', methods=['GET'])
@token_required
def player_phases(id: int):

    phases = PhaseProgress.query.filter_by(player_id=id).all()
    return jsonify({
        'phases': [phase.to_dict() for phase in phases],
        'total': len(phases)
    })


@bp.route('/<int:id>/battles', methods=['GET'])
@token_required
def player_battles(id: int):

    battles: list[Battle] = Battle.query.filter_by(player_id=id).order_by(Battle.created_at.desc()).all()
    return jsonify({
        'battles': [battle.to_dict() for battle in battles],
        'total': len(battles)
    })
