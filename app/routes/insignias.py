from flask import Blueprint, request, jsonify, abort
from ..db import db
from ..models import Insignia
from ..auth import admin_required


bp = Blueprint('insignias', __name__, url_prefix = '/insignias')


@bp.route('/', methods = ['GET'])
def index():
    insignias = Insignia.query.all()
    return jsonify({
        'insignias': [i.to_dict() for i in insignias],
        'total': len(insignias)
    })


@bp.route('/', methods=['POST'])
@admin_required
def create_insignia():
    data = request.get_json()
    if 'name' not in data or 'xp_required' not in data:
        abort(400, description="Campos 'name' e 'xp_required' são obrigatórios")

    if Insignia.query.filter_by(name=data['name']).first():
        abort(400, description="Já existe uma conquista com este nome")

    insignia = Insignia(
        name=data['name'],
        xp_required=data['xp_required'],
        reward_coins=data.get('reward_coins', 0)
    )

    db.session.add(insignia)
    db.session.commit()

    return insignia.to_dict(), 201


@bp.route('/<int:id>', methods = ['GET'])
def get_insignia(id: int):
    insignia: Insignia = Insignia.query.get_or_404(id)
    return insignia.to_dict()


@bp.route('/<int:id>', methods = ['PUT'])
@admin_required
def update_insignia(id: int):

    insignia = Insignia.query.get_or_404(id)
    data = request.get_json()

    if 'name' in data and data['name'] != insignia.name:
        if Insignia.query.filter_by(name=data['name']).first():
            abort(400, description="Já existe uma conquista com este nome")
        insignia.name = data['name']
    
    if 'xp_required' in data:
        insignia.xp_required = data['xp_required']

    if 'reward_coins' in data:
        insignia.reward_coins = data['reward_coins']

    db.session.commit()

    return jsonify({
        'message': f'Conquista {id} atualizada com sucesso.',
        'insignia': insignia.to_dict()
    }), 200


@bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_insignia(id: int):
    insignia = Insignia.query.get_or_404(id)
    db.session.delete(insignia)
    db.session.commit()
    return jsonify({
        'message': f'Conquista {id} deletada com sucesso.'
    }), 200
