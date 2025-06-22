from flask import Blueprint, request, jsonify, abort
from ..db import db
from ..models import Phase


bp = Blueprint('phases', __name__, url_prefix = '/phases')


@bp.route('/')
def phases():
    return jsonify([phase.to_dict() for phase in Phase.query.all()])


@bp.route('/<int:id>')
def phase(id: int):
    return Phase.query.get_or_404(id).to_dict()


@bp.route('/', methods = ['POST'])
def new_phase():
    
    data = request.get_json()
    if not all(key in data for key in ('name', 'boss_id')):
        abort(400, description="Campos 'name' e 'boss_id' são obrigatórios")

    # Atualizado para incluir as novas colunas de recompensa
    phase = Phase(
        name=data['name'],
        boss_id=data['boss_id'],
        reward_coins=data.get('reward_coins', 0),
        reward_experience=data.get('reward_experience', 0)
    )

    db.session.add(phase)
    db.session.commit()

    return phase.to_dict(), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_phase(id: int):

    phase = Phase.query.get_or_404(id)
    data = request.get_json()

    attributes = [
        'name',
        'boss_id',
        'reward_coins',
        'reward_experience'
    ]

    for attr in attributes:
        if attr in data:
            setattr(phase, attr, data[attr])

    db.session.commit()

    return jsonify({
        'message': f'Phase {id} updated successfully.',
        'phase': phase.to_dict()
    }), 200


@bp.route('/<int:id>', methods = ['DELETE'])
def delete_phase(id: int):

    phase = Phase.query.get_or_404(id)
    db.session.delete(phase)
    db.session.commit()

    return jsonify({
        'message': f'Phase {id} deleted successfully.'
    }), 200
