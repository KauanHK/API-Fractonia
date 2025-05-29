from flask import Blueprint, request, jsonify
from ..db import db
from ..models import Boss


bp = Blueprint('bosses', __name__, url_prefix = '/bosses')


@bp.route('/')
def bosses():
    return [boss.to_dict() for boss in Boss.query.all()]


@bp.route('/<int:id>')
def boss(id: int):
    return Boss.query.get_or_404(id).to_dict()


@bp.route('/', methods = ['POST'])
def new_boss():
    
    boss_json = request.get_json()

    boss = Boss(
        name = boss_json['name']
    )

    db.session.add(boss)
    db.session.commit()

    return boss.to_dict()


@bp.route('/<int:id>', methods=['PUT'])
def update_boss(id: int):

    boss = Boss.query.get_or_404(id)

    data_json = request.get_json()

    attributes = [
        'name'
    ]

    for attr in attributes:
        if data_json.get(attr):
            setattr(boss, attr, data_json[attr])

    db.session.commit()

    return jsonify({
        'message': f'Boss {id} updated successfully.',
        'boss': boss.to_dict()
    }), 200


@bp.route('/<int:id>', methods = ['DELETE'])
def delete_boss(id: int):

    boss = Boss.query.get_or_404(id)
    db.session.delete(boss)
    db.session.commit()

    return jsonify({
        'message': f'Boss {id} deleted successfully.'
    })
