from flask import Blueprint, request, jsonify, abort
from ..db import db
from ..models import Achievement
from ..auth import admin_required


bp = Blueprint('achievements', __name__, url_prefix = '/achievements')


@bp.route('/', methods = ['GET'])
def index():
    achievements = Achievement.query.all()
    return jsonify({
        'achievements': [a.to_dict() for a in achievements],
        'total': len(achievements)
    })


@bp.route('/', methods=['POST'])
@admin_required
def create_achievement():
    data = request.get_json()
    if 'name' not in data or 'xp_required' not in data:
        abort(400, description="Campos 'name' e 'xp_required' são obrigatórios")

    if Achievement.query.filter_by(name=data['name']).first():
        abort(400, description="Já existe uma conquista com este nome")

    achievement = Achievement(
        name=data['name'],
        xp_required=data['xp_required'],
        reward_coins=data.get('reward_coins', 0)
    )

    db.session.add(achievement)
    db.session.commit()

    return achievement.to_dict(), 201


@bp.route('/<int:id>', methods = ['GET'])
def get_achievement(id: int):
    achievement: Achievement = Achievement.query.get_or_404(id)
    return achievement.to_dict()


@bp.route('/<int:id>', methods = ['PUT'])
@admin_required
def update_achievement(id: int):

    achievement = Achievement.query.get_or_404(id)
    data = request.get_json()

    if 'name' in data and data['name'] != achievement.name:
        if Achievement.query.filter_by(name=data['name']).first():
            abort(400, description="Já existe uma conquista com este nome")
        achievement.name = data['name']
    
    if 'xp_required' in data:
        achievement.xp_required = data['xp_required']

    if 'reward_coins' in data:
        achievement.reward_coins = data['reward_coins']

    db.session.commit()

    return jsonify({
        'message': f'Conquista {id} atualizada com sucesso.',
        'achievement': achievement.to_dict()
    }), 200


@bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_achievement(id: int):
    achievement = Achievement.query.get_or_404(id)
    db.session.delete(achievement)
    db.session.commit()
    return jsonify({
        'message': f'Conquista {id} deletada com sucesso.'
    }), 200
