from flask import Blueprint, request
from ..db import db
from ..models import Phase


bp = Blueprint('phase', __name__, url_prefix = '/phase')


@bp.route('/all')
def phases():
    return [phase.to_dict() for phase in Phase.query.all()]


@bp.route('/<int:id>')
def phase(id: int):
    return Phase.query.get_or_404(id).to_dict()


@bp.route('/new', methods = ['POST'])
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
