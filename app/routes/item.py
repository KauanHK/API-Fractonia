from flask import Blueprint, request
from ..db import db
from ..models import Item


bp = Blueprint('item', __name__, url_prefix = '/item')


@bp.route('/all')
def items():
    return [item.to_dict() for item in Item.query.all()]


@bp.route('/<int:id>')
def item(id: int):
    return Item.query.get_or_404(id)


@bp.route('/new', methods = ['POST'])
def new_item():
    
    print('starting')
    item_json = request.get_json()

    print('success json')
    item = Item(
        name = item_json['name'],
        description = item_json['description'],
        rarity_id = item_json['rarity_id'],
        power = item_json.get('power')
    )
    print(item)

    db.session.add(item)
    db.session.commit()

    return item.to_dict()
