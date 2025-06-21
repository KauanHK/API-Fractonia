from flask import Blueprint, request, jsonify
from ..db import db
from ..models import Battle, ResultType


bp = Blueprint('battles', __name__, url_prefix='/battles')


@bp.route('/')
def list_battles():
    battles = Battle.query.all()
    return jsonify([battle.to_dict() for battle in battles])


@bp.route('/<int:id>')
def get_battle(id: int):
    return Battle.query.get_or_404(id).to_dict()


@bp.route('/', methods = ['POST'])
def create_battle():
    data = request.get_json()

    battle = Battle(
        player_id = data['player_id'],
        boss_id = data.get('boss_id'),
        result = ResultType(data.get('result', 'win'))
    )

    db.session.add(battle)
    db.session.commit()

    return battle.to_dict(), 201


@bp.route('/<int:id>', methods = ['PUT'])
def update_battle(id: int):
    battle = Battle.query.get_or_404(id)
    data = request.get_json()

    if 'player_id' in data:
        battle.player_id = data['player_id']
    if 'boss_id' in data:
        battle.boss_id = data['boss_id']
    if 'result' in data:
        battle.result = ResultType(data['result'])

    db.session.commit()

    return jsonify({
        'message': f'Battle {id} updated successfully.',
        'battle': battle.to_dict()
    }), 200


@bp.route('/<int:id>', methods = ['DELETE'])
def delete_battle(id: int):
    battle = Battle.query.get_or_404(id)
    db.session.delete(battle)
    db.session.commit()

    return jsonify({
        'message': f'Battle {id} deleted successfully.'
    }), 200
