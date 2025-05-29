from flask import Blueprint, request, jsonify
from ..db import db
from ..models import Phase


bp = Blueprint('phases', __name__, url_prefix = '/phases')


@bp.route('/')
def phases():
    return [phase.to_dict() for phase in Phase.query.all()]


@bp.route('/<int:id>')
def phase(id: int):
    return Phase.query.get_or_404(id).to_dict()


@bp.route('/', methods = ['POST'])
def new_item():
    
    phase_json = request.get_json()

    phase = Phase(
        name = phase_json['name'],
        description = phase_json['description'],
        boss_id = phase_json['boss_id']
    )

    db.session.add(phase)
    db.session.commit()

    return phase.to_dict()


@bp.route('/<int:id>', methods=['PUT'])
def update_phase(id: int):

    phase = Phase.query.get_or_404(id)

    data_json = request.get_json()

    attributes = [
        'name',
        'description',
        'boss_id'
    ]

    for attr in attributes:
        if data_json.get(attr):
            setattr(phase, attr, data_json[attr])

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
    })
