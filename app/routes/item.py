from flask import Blueprint, request, jsonify
from ..db import db
from ..models import Item


bp = Blueprint('items', __name__, url_prefix = '/items')


@bp.route('/')
def items():
    return [item.to_dict() for item in Item.query.all()]


@bp.route('/<int:id>')
def item(id: int):
    return Item.query.get_or_404(id).to_dict()


@bp.route('/', methods = ['POST'])
def new_item():
    
    item_json = request.get_json()

    item = Item(
        name = item_json['name'],
        description = item_json['description'],
        rarity_id = item_json['rarity_id'],
        power = item_json.get('power')
    )

    db.session.add(item)
    db.session.commit()

    return item.to_dict()


@bp.route('/<int:id>', methods=['PUT'])
def update_item(id: int):

    item = Item.query.get_or_404(id)

    data_json = request.get_json()

    attributes = [
        'name',
        'description',
        'power',
        'rarity_id'
        'acquired_at',
    ]

    for attr in attributes:
        if data_json.get(attr):
            setattr(item, attr, data_json[attr])

    db.session.commit()

    return jsonify({
        'message': f'Item {id} updated successfully.',
        'item': item.to_dict()
    }), 200


@bp.route('/<int:id>', methods = ['DELETE'])
def delete_item(id: int):

    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()

    return jsonify({
        'message': f'Item {id} deleted successfully.'
    })
