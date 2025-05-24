from flask import Blueprint, request
from ..db import db
from ..models import Rarity


bp = Blueprint('rarity', __name__, url_prefix = '/rarity')


@bp.route('/all')
def rarities():
    return [boss.to_dict() for boss in Rarity.query.all()]


@bp.route('/<int:id>')
def rarity(id: int):
    return Rarity.query.get_or_404(id).to_dict()


@bp.route('/new', methods = ['POST'])
def new_rarity():
    
    rarity_json = request.get_json()

    rarity = Rarity(
        name = rarity_json['name'],
        color = rarity_json['color'],
        description = rarity_json.get('description')
    )

    db.session.add(rarity)
    db.session.commit()

    return rarity.to_dict()
