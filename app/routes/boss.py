from flask import Blueprint, request
from ..db import db
from ..models import Boss


bp = Blueprint('boss', __name__, url_prefix = '/boss')


@bp.route('/all')
def bosses():
    return [boss.to_dict() for boss in Boss.query.all()]


@bp.route('/<int:id>')
def boss(id: int):
    return Boss.query.get_or_404(id).to_dict()


@bp.route('/new', methods = ['POST'])
def new_boss():
    
    boss_json = request.get_json()

    boss = Boss(
        name = boss_json['name']
    )

    db.session.add(boss)
    db.session.commit()

    return boss.to_dict()
