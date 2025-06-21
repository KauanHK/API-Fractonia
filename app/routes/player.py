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

    achievement_xp_tiers: list[Achievement] = Achievement.query.all()

    # IDs das conquistas que o jogador já tem
    player_achievements_ids: list[int] = {pa.id for pa in player.achievements}

    for achievement in achievement_xp_tiers:
        
        # Verifica se o jogador tem XP suficiente e ainda não possui a conquista
        if player.experience >= achievement.xp and achievement.id not in player_achievements_ids:
            
            # Concede a nova conquista
            new_player_achievement = PlayerAchievement(
                player_id = player.id,
                achievement_id = achievement.id
            )
            db.session.add(new_player_achievement)
            print(f"Conquista '{achievement.name}' concedida ao jogador {player.username} por atingir {achievement.xp} XP!")

            # Aplica as recompensas da própria conquista
            achievement_def: Achievement = Achievement.query.get(achievement.id)
            if achievement_def:
                player.coins += achievement_def.reward_coins


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
    players: list[Player] = Player.query.order_by(Player.experience.desc(), Player.level.desc()).all()
    return jsonify([
        {
            'rank': index + 1,
            'id': player.id,
            'username': player.username,
            'level': player.level,
            'experience': player.experience
        }
        for index, player in enumerate(players)
    ])


@bp.route('/<int:id>/phases', methods=['POST'])
@token_required
def complete_phase(id: int):
    """Registra a conclusão de uma fase, aplica recompensas e verifica conquistas."""
    validate_access(id)
    data = request.get_json()
    if 'phase_id' not in data:
        abort(400, description="O ID da fase é obrigatório")

    player = Player.query.get_or_404(id)
    phase_id = data['phase_id']
    phase = Phase.query.get_or_404(phase_id)
    
    # Verifica se o jogador já completou esta fase
    existing = PhaseProgress.query.filter_by(
        player_id=id,
        phase_id=phase_id
    ).first()
    
    if existing:
        return jsonify({
            'message': 'Fase já completada anteriormente',
            'progress': existing.to_dict()
        }), 200
    
    # Adiciona as recompensas da fase (XP e Moedas) ao jogador
    if phase.reward_coins:
        player.coins += phase.reward_coins
    if phase.reward_experience:
        player.experience += phase.reward_experience

    # Após ganhar XP, verifica se alguma conquista foi desbloqueada
    _check_and_grant_achievements(player)
    
    # Cria o registro de progresso da fase
    progress = PhaseProgress(
        player_id=id,
        phase_id=phase_id,
        completed=True,
        completed_at=datetime.utcnow()
    )
    db.session.add(progress)
    db.session.commit()
    
    return jsonify({
        'message': f'Fase {phase.name} completada! Recompensas recebidas.',
        'progress': progress.to_dict(),
        'player_status': player.to_dict() # Retorna o status atualizado do jogador
    }), 201


# --- OUTRAS ROTAS (sem alterações na lógica principal) ---

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
    validate_access(id)
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
        for attr in ('level', 'experience', 'coins'):
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
    validate_access(id)
    player: Player = Player.query.get_or_404(id)
    return player.to_dict()


@bp.route('/<int:id>/items')
@token_required
def player_items(id: int):
    validate_access(id)
    items: list[Item] = PlayerItem.query.filter_by(player_id = id)
    return jsonify({
        'items': [item.to_dict() for item in items],
        'total': items.count()
    })


@bp.route('/<int:id>/items', methods=['POST'])
@token_required
def add_player_item(id: int):
    validate_access(id)
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
    validate_access(id)
    player_item = PlayerItem.query.filter_by(player_id=id, item_id=item_id).first_or_404()
    db.session.delete(player_item)
    db.session.commit()
    return jsonify({
        'message': f'Item {item_id} removido do jogador {id} com sucesso.'
    }), 200


@bp.route('/<int:id>/achievements')
@token_required
def player_achievements(id: int):
    validate_access(id)
    Player.query.get_or_404(id)
    achievements: list[Achievement] = PlayerAchievement.query.filter_by(player_id=id).all()
    return jsonify([achievement.to_dict() for achievement in achievements])


@bp.route('/<int:id>/battles', methods=['POST'])
@token_required
def record_battle(id: int):
    validate_access(id)
    data = request.get_json()
    if 'result' not in data:
        abort(400, description="O resultado ('result') da batalha é obrigatório")
    battle = Battle(
        player_id=id,
        result=data['result'],
        boss_id=data.get('boss_id')
    )
    db.session.add(battle)
    db.session.commit()
    return jsonify({
        'message': 'Batalha registrada com sucesso',
        'battle': battle.to_dict()
    }), 201


@bp.route('/<int:id>/phases', methods=['GET'])
@token_required
def player_phases(id: int):
    validate_access(id)
    phases = PhaseProgress.query.filter_by(player_id=id).all()
    return jsonify({
        'phases': [phase.to_dict() for phase in phases],
        'total': len(phases)
    })


@bp.route('/<int:id>/battles', methods=['GET'])
@token_required
def player_battles(id: int):
    validate_access(id)
    battles: list[Battle] = Battle.query.filter_by(player_id=id).order_by(Battle.created_at.desc()).all()
    return jsonify({
        'battles': [battle.to_dict() for battle in battles],
        'total': len(battles)
    })
